<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
	<script src="./jquery/jquery-1.3.2.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery-ui-1.7.2.custom.min.js" type="text/javascript"></script>
	<script src="./jquery/jquery.query.js" type="text/javascript"></script>
	<script src="./js/jquery.selector.js" type="text/javascript"></script>
	<script src="./js/lucullus.js"	 type="text/javascript"></script>
	<script src="./js/lucullus.seqgui.js"	type="text/javascript"></script>
	<script src="./js/lucullus.ui.js"	type="text/javascript"></script>
	<script src="./js/lucullus.gui.js"	type="text/javascript"></script>

	<!-- <link type="text/css" href="./jquery/smoothness/jquery-ui-1.7.2.custom.css" rel="stylesheet" /> -->
	<link type="text/css" href="./jquery/lightness/jquery-ui-1.7.2.custom.css" rel="stylesheet" />
	<link type="text/css" href="./css/main.css" rel="stylesheet" />
	<link type="text/css" href="./css/lucullus.css" rel="stylesheet" />

    <link rel="stylesheet" type="text/css" href="js/ext/resources/css/ext-all.css" />
 	<script type="text/javascript" src="js/ext/adapter/jquery/ext-jquery-adapter.js"></script>
    <script type="text/javascript" src="js/ext/ext-all.js"></script>


	<title>Lucullus bla</title>
</head>
<body>
	<div align="center">
		<table border="0" cellspacing="0" cellpadding="0">
			<tr>
				<td colspan="2">
					<div id="header"><img src="img/layout/lucullus_logo.png" alt="lucullus" /></div>
					<ul id="menu">	
						<li style="background-color: #999999"><a href="index.html">Home</a></li>
						<li><a href="docu.html">Documentation</a></li>
						<li><a href="contact.html">Contact</a></li>
					</ul>
				</td>
			</tr>

			<tr>
				<td width="750px">
					<div id="headline"><div><div>&#160;</div></div></div>
				</td>
				<td width="150px">
				</td>
			</tr>
			<tr>
				<td class="leftrow">
					<div id="content">
						<h2>Demo</h2><p style="padding: 0px 5px 20px 10px;">
							<button id='new_seq_window'>New Sequence Window</button>
							<button id='new_newick_window'>New Newick Window</button>
							<button id='new_ext_window'>New Ext Window (development)</button>
						</p>
						<h2>Systems Biology</h2><p style="padding: 0px 5px 20px 10px;">Biology is currently experiencing a paradigm shift - from studying individual genes and proteins towards analysing the structure and function of gene and protein networks. We are interested in understanding motor protein mediated processes in eukaryotic cells that are essential for muscle function, neuronal transport, cell division and others, at a systems level. Over the past few years, we have developed experimental methodologies to gain insight into the function of the dynein/dynactin motor protein complex at atomic resolution, and computational methods to determine the motor protein content of the eukaryotes.</p>
						<h2>Bioinformatics</h2><p style="padding: 0px 5px 20px 10px;">The basis for the understanding of intracellular transport in eukaryotes at a cellular or organismal level is the determination of the motor protein content of the genomes. In this respect we highly profit from the continuously increasing amount of finished genome sequences. However, the process of genome annotation still lags considerably behind that of genome data generation. But it is the annotation that connects the sequence to the biology of the organism. Thus, we manually annotate the motor proteins using the possibilities of comparative genomics and multiple sequence alignments. To cope with the exponentially increasing amount of data we develop database and gene determination tools.</p>
						<h2>Biochemistry / Structural Biology</h2><p style="padding: 0px 5px 20px 5px;">To understand the function of the motor proteins at atomic resolution we need precise models. A few kinesin and myosin crystal structures are available, but high-resolution data for the dynein/dynactin complex is still missing. Therefore, we are developing methods for the production of difficult-to-express proteins. For this purpose we are mainly using the lower eukaryote <i>Dictyostelium discoideum</i>.</p>
					</div>
				</td>
				<td id="rightrow">
					<div><a href="http://www.motorprotein.de" target="motorprotein"><img src="img/layout/motorprotein_link.png" alt="Motorprotein.de" /></a></div>
					<div style="padding-top: 5px"><a href="http://www.diark.org" target="diark"><img src="img/layout/diark_link.png" alt="link to diark" /></a></div>
					<div style="padding-top: 5px"><a href="http://www.cymobase.org" target="cymobase"><img src="img/layout/cymobase_link.png" alt="link to cymobase" /></a></div>
					<div style="padding-top: 5px"><a href="http://www.webscipio.org" target="scipio"><img src="img/layout/scipio_link.png" alt="link to scipio" /></a></div>
					<div style="padding-top: 20px"><a href="http://www.mpg.de" target="mpg"><img src="img/layout/mpg.png" alt="MPG" /></a></div>
					<div style="padding-top: 5px"><a href="http://www.mpibpc.mpg.de" target="mpibpc"><img src="img/layout/mpibpc.png" alt="MPI for biophysical chemistry" /></a></div>
				</td>
			</tr>
			<tr>
				<td>
					<div id="baseline"><div><div>&#160;</div></div></div>
				</td>
				<td />
			</tr>
			<tr>
				<td>
					<div id="footer">&#169; Motorprotein.de 2010 | <a class="external" href="http://www.mpibpc.gwdg.de/metanavi/impressum/index.html" target="foobar">Impressum</a>
					<a href="http://www.mozilla.org/products/firefox" target="foobar"><img src="img/layout/firefox2b.gif" alt="" /></a></div>
				</td>
				<td />
			</tr>
		</table>
	</div>

	<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
	</script>
	<script type="text/javascript">
	_uacct = "UA-382946-4";
	urchinTracker();
	</script>

	<script type="text/javascript">
	var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
	document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
	</script>
	<script type="text/javascript">
	var pageTracker = _gat._getTracker("UA-9383624-2");
	pageTracker._initData();
	pageTracker._trackPageview();
	</script>

	<script type="text/javascript">
		var server = document.location.protocol + '//' + document.location.host + document.location.pathname + 'api'
		var api = new Lucullus.api(server, "test")
		var gui = []
		/* api calls are blocking. Never call them in main thread */
		$('#new_seq_window').bind('click', function () {
			gui[gui.length] = new SeqGui(api)
		})
		$('#new_newick_window').bind('click', function () {
			gui[gui.length] = new Lucullus.ui.Newick(api)
		})
		
		
		
	
		/*!
		 * Ext JS Library 3.1.0
		 * Copyright(c) 2006-2009 Ext JS, LLC
		 * licensing@extjs.com
		 * http://www.extjs.com/license
		 */
		Ext.onReady(function(){
		    var button = Ext.get('new_ext_window');
		    button.on('click', function(){
		        // Panel for the west
				var nav = new Ext.Toolbar()
				nav.add({text:'test'})

		        var idx = new Ext.Panel({
		            title: 'Sequence Index',
		            region: 'west',
		            split: true,
		            width: 200,
		            collapsible: true,
		            margins:'0 0 0 0',
		            cmargins:'0 0 0 0'
		        });

		        // Panel for the west
		        var dta = new Ext.Panel({
		            title: 'Phylogenetic Tree Data',
		            region: 'center',
		            split: true,
		            width: 400,
		            collapsible: false,
		            margins:'0 0 0 0',
		            cmargins:'0 0 0 0'
		        });

		        var win = new Ext.Window({
		            title: 'Layout Window',
		            closable:true,
		            width:600,
		            height:350,
		            //border:false,
		            plain:true,
					layout:'border',
					defaults: {
					    split: true,
					    bodyStyle: 'padding:0px'
					},
					tbar: nav,
					items: [idx, dta]
		        });
		        win.show(this);
				$(dta.body.dom).html('...')

		    });
		});
		</script>

</body>
</html>

