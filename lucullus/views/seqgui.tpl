<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<script src="./jquery/jquery-1.3.2.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery.query.js" type="text/javascript"></script>

	<script src="./jquery/jquery-ui-1.7.2.custom.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery-ui-1.7.2.custom.min.js" type="text/javascript"></script>
	<link type="text/css" href="./jquery/jquery-ui-1.7.2.custom.css" rel="stylesheet" />

	<script src="./js/lucullus.js"	 type="text/javascript"></script>
	<script src="./js/lucullus.seqgui.js"	type="text/javascript"></script>
	<title>Lucullus</title>
</head>
<body>
	<div id="debug"></div>
	<div id="seqgui" style="width: 90%">
		<div class="upload" title="Upload data">
			<form style="width: 500px">
				<label for="upUrl">URL:</label> <input type="text" name="upUrl" /><input type="submit" value="Upload"/><br />
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
				<div class="status"></div>
			</form>
		</div>
		
		<table class="guitable" style="height:500px; width:100%; margin: auto; border: 1px solid grey; border-spacing:0px; border-collapse:collapse">
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
		</table>
		<div class="status">Please activate JavaScript.</div>
		<div class="slider"></div>
		<form class='search'>Suche: <input type='text' name='q' /></form>
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

