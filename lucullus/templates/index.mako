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
		<form class='upload'>
			<div style="color: green">
				Your Lucullus project is currently empty. Please provide an URL to a fasta file.
			</div>
		  URL: <input type="text" name="upUrl" />
		  Format:<select>
		    <option value="fasta">Fasta</option>
		  </select> <input type="submit" value="Upload"/>
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
			
			this.status_node = $('tr.status td.text:first', this.root)
			this.upload_node = $('form.upload:first', this.root)
			this.node_main = $('tr.main:first', this.root)
			this.node_compare = $('tr.compare:first', this.root)
			this.node_control = $('tr.control:first', this.root)
			this.node_status = $('tr.status:first', this.root)
			this.node_status_text = $('tr.status td.text:first', this.root)
			this.node_main_map = $('tr.main td.map:first', this.root)
			this.node_main_index = $('tr.main td.index:first', this.root)
			
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
			var txt = this.api.create('TextResource')
			var seq = this.api.create('SequenceResource')
			var view = this.api.create('SequenceView')
			var iview = this.api.create("IndexView")
			//var rview = this.api.create("RulerView")

			// The following code blocks have do be called (and completed) in order.
			// To do this, we /could/ use nested wait() blocks. But thats ugly.
			
			// Upload the textfile
			var upload_txt = function(c) {
				if(txt.error) { self.status('Creation of text Buffer failed'); return }
				if(seq.error) { self.status('Creation of sequence Buffer failed'); return }
				if(view.error) { self.status('Creation of image Buffer failed'); return }
				if(iview.error) { self.status('Creation of index Buffer failed'); return }
				txt.load({'uri':file})
				txt.wait(parse_seq)
			}

			// Parse the textfile
			var parse_seq = function(c) {
				if(txt.error) { self.status('Upload failed: '+txt.error.message); return }
				self.status('Upload complete. Filesize: '+txt.size+' bytes')
				seq.load({'source':txt.id})
				seq.wait(load_into_views)
			}

			// Load sequences into views
			var load_into_views = function(c) {
				if(seq.error) { self.status('Parser error: '+seq.error.message); return }
				self.status('Parsing complete. Number of sequences: '+seq.len)
				self.upload_node.hide()
				self.sequence = seq
				view.load({'source':seq.id})
				iview.load({'source':seq.id})
				view.wait(create_seqmap)
			}

			// Draw sequence map and configure index view
			var create_seqmap = function(c) {
				if(view.error) { self.status('View error: '+view.error.message); return }
				self.status('Rendering complete. Number of sequences: '+seq.len)
				var node = $('tr.main td.map:first', this.root)
				$('tr.main', this.root).show()
				var map = new Lucullus.PixelMap(node, function(numberx, numbery, sizex, sizey) {
						return self.api.server + '/' + self.api.session + '/' + view.id + '/render?x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey
				})
				map.set_clipping(0,0,view.width, view.height)
				map.set_size(node.width(),node.height())
				self.ml.addMap(map,1,1)
				self.ml.addLinear(node,1,1)
				self.api.test = iview
				iview.set({'lineheight':view.fieldsize})
				iview.wait(create_indexmap)
			}

			// Draw index view
			var create_indexmap = function(c) {
				if(iview.error) { self.status('View error: '+iview.error.message); return }
				self.status('Index complete. Number of rows: '+iview.rows)
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

			// Wait for resource creation and start it all!
			Lucullus.wait([txt,seq,view,iview], upload_txt)
		}
		

		
		
		var autoload = jQuery.query.get('autoload')
		var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
		var api
		var gui

	  /* api calls are blocking. Never call them in main thread */
		$(document).ready(function() {
			api = new Lucullus.api(server, "nokey")
			gui = new SeqGui(api, '#seqgui')

			api.connect()

			if(autoload)
			  gui.upload(autoload, 'fasta')
		})
	
	</script>
</body>
</html>
