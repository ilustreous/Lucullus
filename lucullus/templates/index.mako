<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<script src="./js/jquery.js" type="text/javascript"></script>
	<script src="./js/jquery.query.js" type="text/javascript"></script>
	<script src="./js/lucullus.js"   type="text/javascript"></script>
	<script src="./js/lucullus.seqgui.js"   type="text/javascript"></script>
	<title>Lucullus</title>
	<style type="text/css">
		html {background-color:#fff}
		#mySeqMap {background-color:#eee}
	</style>
</head>
<body>
	<div id="debug"></div>
	<div id="seqgui">
		<form class='upload' style="background: lightgrey;
									border: 5px solid grey;
									position: absolute; top:50%; left:50%;
									height:100px; width:400px; padding:14px;
									margin:-65px -215px;
									-moz-border-radius: 10px 10px;
									overflow:hidden">
			<div style="font-weight: bold; border-bottom: 1px solid grey; margin-bottom:5px">Upload a fasta File</div>
			<label for="upUrl">URL:</label> <input type="text" name="upUrl" style="width: 50%" /> <input type="submit" value="Upload"/><br />
			<label for="format">Format:</label>
			<select name="format">
		    	<option value="fasta">Fasta</option>
			</select>
			<select name="pack">
		    	<option value="none">Not compressed</option>
		    	<option value="gz">gzip</option>
		    	<option value="rar">rar</option>
		    	<option value="zip">zip</option>
			</select>
			<div style="color:red" class="status"></div>
		</form>
		<table class="guitable" style="width: 860px; height: 500px; margin: auto; border: 1px solid grey; border-spacing:0px; border-collapse:collapse">
			<tr class="control" style="height:20px">
				<td class="logo"></td>
				<td class="ruler"></td>
			</tr>
			<tr class="compare" style="height:14px">
				<td class="index"></td>
				<td class="map"></td>
			</tr>
			<tr class="main">
				<td class="index" style="width:100px"></td>
				<td class="map"></td>
			</tr>
			<tr class="status" style="height:20px">
				<td colspan='2' class="text" style="border: 1px solid grey">Please activate JavaScript.</td>
			</tr>
		</table>
  </div>
	<script type="text/javascript">
	  /*<![CDATA[*/
		function SeqGui(api, root) {
			var self = this
			this.api = api
			this.root = root
			this.ml = new Lucullus.MoveListenerFactory()
			
			this.sequence = null
			this.compare = null
			
			this.sequence_view = null
			this.compare_view = null
			
			$('tr', this.root).hide()
			$('tr td', this.root).css('padding','0px')
			$('tr.status', this.root).show()
			
			this.status('Preparing...')
			
			$('form.upload:first', this.root).bind('submit', function(event) {
				event.preventDefault()
				event.stopPropagation()
				var file = $('input:first',event.target).val()
				var format = $('select:first',event.target).val()
				self.upload(file, format)
			})
			
			this.status('Waiting for sequence upload...')
		}
		
		SeqGui.prototype.status = function(txt) {
			$('tr.status td.text:first', this.root).html(txt)
		}
		
		SeqGui.prototype.upload = function(file, format){
			this.status('Starting Upload. File: '+file+' Format: '+format)
			var self = this
			// Request resources
			var txt = this.api.create('TextResource','tr')
			var seq = this.api.create('SequenceResource','seq')
			var view = this.api.create('SequenceView','sev')
			var iview = this.api.create("IndexView",'iv')
			var rview = this.api.create("RulerView",'rv')
			//var rview = this.api.create("RulerView")

			// The following code blocks have do be called (and completed) in order.
			// To do this, we /could/ use nested wait() blocks. But thats ugly.
			
			// Upload the textfile
			var upload_txt = function(c) {
				if(txt.error) { self.status('Creation of text Buffer failed'); return }
				if(seq.error) { self.status('Creation of sequence Buffer failed'); return }
				if(view.error) { self.status('Creation of image Buffer failed'); return }
				if(iview.error) { self.status('Creation of index Buffer failed'); return }
				if(rview.error) { self.status('Creation of index Buffer failed'); return }
				txt.load({'uri':file})
				txt.wait(parse_seq)
			}

			// Parse the textfile
			var parse_seq = function(c) {
				if(txt.error) {
					self.status('Upload failed: '+txt.error.message);
					$('form.upload', this.root).css('border-color','red')
					$('form.upload .status', this.root).html(txt.error.message)
					return
				}
				$('form.upload', this.root).css('border-color','green')
				self.status('Upload complete. Filesize: '+txt.size+' bytes')
				seq.load({'source':txt.id})
				seq.wait(load_into_views)
			}

			// Load sequences into views
			var load_into_views = function(c) {
				if(seq.error) { self.status('Parser error: '+seq.error.message); return }
				self.status('Parsing complete. Number of sequences: '+seq.len)
				self.sequence = seq
				view.load({'source':seq.id})
				view.set({'fieldsize': 14})
				iview.load({'source':seq.id})
				iview.set({'lineheight': 14})
				rview.set({'step': 14})
				view.wait(create_seqmap)
				iview.wait(create_indexmap)
				Lucullus.wait([view,rview], create_rulermap)
			}

			// Draw sequence map and configure index view
			var create_seqmap = function(c) {
				if(view.error) { self.status('View error: '+view.error.message); return }
				self.status('Rendering complete. Number of sequences: '+seq.len)
				var node = $('tr.main td.map:first', this.root)
				$('tr.main', this.root).show()
				$('form.upload', this.root).hide()
				var map = new Lucullus.PixelMap(node, function(numberx, numbery, sizex, sizey) {
						return self.api.server + '/' + self.api.session + '/' + view.id + '/render?x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey
				})
				map.set_clipping(0,0,view.width, view.height)
				map.set_size(node.width(),node.height())
				self.ml.addMap(map,1,1)
				self.ml.addLinear(node,1,1)
				self.api.test = iview
			}

			// Draw index view
			var create_indexmap = function(c) {
				if(iview.error) { self.status('View error: '+iview.error.message); return }
				var node = $('tr.main td.index:first', this.root)
				$('tr.main', this.root).show()
				var map2 = new Lucullus.PixelMap(node, function(numberx, numbery, sizex, sizey) {
						return self.api.server + '/' + self.api.session + '/' + iview.id + '/render?x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey
				})
				map2.set_clipping(0,0,iview.width,iview.height)
				map2.set_size(node.width(),node.height())
				self.ml.addMap(map2,0,1)
				self.ml.addLinear(node,0,1)
			}

			// Draw ruler view
			var create_rulermap = function(c) {
				if(rview.error) { self.status('View error: '+rview.error.message); return }
				var node = $('tr.control td.ruler:first', this.root)
				$('tr.control', this.root).show()
				var map3 = new Lucullus.PixelMap(node, function(numberx, numbery, sizex, sizey) {
						return self.api.server + '/' + self.api.session + '/' + rview.id + '/render?x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey
				})
				map3.set_clipping(view.offset[0],rview.offset[1],view.width+view.offset[0],rview.height+rview.offset[1])
				map3.set_size(node.width(),node.height())
				self.ml.addMap(map3,1,0)
				self.ml.addLinear(node,1,0)
			}

			// Wait for resource creation and start it all!
			Lucullus.wait([txt,seq,view,iview, rview], upload_txt)
		}
		

		
		
		var autoload = jQuery.query.get('upUrl')
		var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
		var api
		var gui

	  /* api calls are blocking. Never call them in main thread */
		$(document).ready(function() {
			api = new Lucullus.api(server, "nokey")
			gui = new SeqGui(api, '#seqgui')

			api.connect().wait(function(){
				if(autoload)
					gui.upload(autoload, 'fasta')
			})
		})
	
	</script>
</body>
</html>
