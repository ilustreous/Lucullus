<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<script src="./js/jquery.js" type="text/javascript"></script>
	<script src="./js/jquery.query.js" type="text/javascript"></script>
	<script src="./js/lucullus.js"	 type="text/javascript"></script>
	<script src="./js/lucullus.seqgui.js"	type="text/javascript"></script>
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
		<table class="guitable" style="height:500px; width: 90%; margin: auto; border: 1px solid grey; border-spacing:0px; border-collapse:collapse">
			<tr class="control" style="height:20px">
				<td class="logo" style="width: 100px">logo</td>
				<td class="ruler"></td>
			</tr>
			<tr class="compare" style="height:14px">
				<td class="index" style="width: 100px"></td>
				<td class="map"></td>
			</tr>
			<tr class="main">
				<td class="index" style="width: 100px"></td>
				<td class="map"></td>
			</tr>
			<tr class="status" style="height:20px">
				<td colspan='2' class="text" style="border: 1px solid grey">Please activate JavaScript.</td>
			</tr>
		</table>
		<select id='seqjump' name='seqjump'>
		</select>
  </div>
	<script type="text/javascript">
	  /*<![CDATA[*/
	var autoload = jQuery.query.get('upUrl')
	var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
	var api
	var gui
		/* api calls are blocking. Never call them in main thread */
	$(document).ready(function() {
		api = new Lucullus.api(server, "test")
		gui = new SeqGui(api, '#seqgui')
	})
	/*]]>*/</script>
</body>
</html>

