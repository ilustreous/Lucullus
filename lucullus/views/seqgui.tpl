<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<script src="./jquery/jquery-1.3.2.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery-ui-1.7.2.custom.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery.query.js" type="text/javascript"></script>
	<script src="./js/lucullus.js"	 type="text/javascript"></script>
	<script src="./js/lucullus.seqgui.js"	type="text/javascript"></script>

	<!-- <link type="text/css" href="./jquery/smoothness/jquery-ui-1.7.2.custom.css" rel="stylesheet" /> -->
	<link type="text/css" href="./jquery/lightness/jquery-ui-1.7.2.custom.css" rel="stylesheet" />
	<link type="text/css" href="./css/main.css" rel="stylesheet" />

	<title>Lucullus</title>
</head>
<body>
	<script type="text/javascript">
	  /*<![CDATA[*/
	var autoload = jQuery.query.get('upUrl')
	var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
	var api
	var gui
		/* api calls are blocking. Never call them in main thread */
	$(window).load(function () {
		if(autoload) $('input[name="upUrl"]').val(autoload)
		api = new Lucullus.api(server, "test")
		gui = new SeqGui(api)
	})
	/*]]>*/</script>
</body>
</html>

