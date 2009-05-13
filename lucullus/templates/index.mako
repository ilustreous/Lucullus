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
		<form id='seqgui-upload'>
			<div style="color: green">
				Your Lucullus project is currently empty. Please provide an URL to a fasta file.
			</div>
		  URL: <input type="text" name="upUrl" />
		  Format:<select>
		    <option value="fasta">Fasta</option>
		  </select> <input type="submit" value="Upload"/>
		</form>
		<table id="seqgui-table" style="width: 860px; height: 500px; margin: auto; border: 1px solid grey">
			<tr style="height:20px">
				<td style="width:100px"></td>
				<td></td>
			</tr>
			<tr style="height:14px">
				<td></td>
				<td></td>
			</tr>
			<tr>
				<td></td>
				<td></td>
			</tr>
		</table>
		<div id="seqgui-status" style="border: 1px solid grey">Please activate JavaScript.</div>
  </div>
	<div style="width: 850px; margin: 10px auto">
		<a onclick="$('#help').toggle()">Help (show/hide)</a>
		<div style="display: none; background-color: #ffffee; padding: 15px" id="help">
			
		</div>
	</div>
	<script type="text/javascript">
	  /*<![CDATA[*/
		function SeqGui(api, ns) {
			var self = this
			this.api = api
			this.ns = ns
			this.root_node = $(this.ns)[0]
			this.status_node = $(this.ns+'-status:first')
			this.upload_node = $(this.ns+'-upload:first')
			this.table_node = $(this.ns+'-table:first')
			this.map_nodes = $(this.ns+'-table td')
			
			this.sequence = null
			this.compare = null
			
			this.sequence_view = null
			this.compare_view = null
			
			this.status_node.show()
			this.upload_node.show()
			this.table_node.hide()
			this.status('Preparing...')
			
			this.upload_node.bind('submit', function(event) {
				event.preventDefault()
				event.stopPropagation()
				var file = $('input:first',event.target).val()
				var format = $('select:first',event.target).val()
				self.upload(file, format)
			})
			
			this.status('Waiting for sequence upload...')
		}
		
		SeqGui.prototype.status = function(txt) {
			this.status_node.html(txt)
		}
		
		SeqGui.prototype.upload = function(file, format){
			this.status('Starting Upload. File: '+file+' Format: '+format)

		  // Prepare a textfile
			var txt = this.api.create('TextResource')
			if(txt.error) {
				this.status('Error: '+txt.error.message)
				return
			}

			// Upload textfile
			txt.load({uri:file})
			if(txt.error) {
				this.status('Error: '+txt.error.message)
				return
			}
			
			this.status('Upload complete. Filesize: '+txt.result.size+' bytes')
			// Create sequence container
			var seq = this.api.create("SequenceResource")
			if(seq.error) {
				this.status('Server error: ' +seq.error.message)
				return
			}
			
			// Parse file
			seq.load({'source':txt.id})
			if(seq.error) {
				this.status('Parser error: ' +seq.error.message)
				return
			}

			this.status('Parsing complete. Number of sequences: '+seq.result.len)
			this.sequence = seq

			// Create sequence view
			var view = this.api.create("SequenceView")
			if(view.error) {
				this.status('Server error: ' +seq.error.message)
				return
			}
			
			// Load sequences into vier
			view.load({'source':seq.id})
			if(view.error) {
				this.status('View error: ' +seq.error.message)
				return
			}
			
			this.status('Rendering complete. Number of sequences: '+seq.result.len)
			this.sequence_view = view
			
			var map = new Lucullus.PixelMap(this.map_nodes[5], function(numberx, numbery, sizex, sizey) {
					return api.server + '/' + api.session + '/' + view.id + '/render?x='+(numberx*sizex)+'&y='+(numbery*sizey)+'&w='+sizex+'&h='+sizey	
			})
			this.table_node.show()
			map.set_clipping(0,0,view.result['width'],view.result['height'])
			map.set_size($(this.map_nodes[5]).width(),$(this.map_nodes[5]).height()) 
			this.upload_node.hide()
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
