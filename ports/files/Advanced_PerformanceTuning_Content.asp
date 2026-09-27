<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta HTTP-EQUIV="Pragma" CONTENT="no-cache">
<meta HTTP-EQUIV="Expires" CONTENT="-1">
<meta http-equiv="X-UA-Compatible" content="IE=Edge" />
<link rel="shortcut icon" href="images/favicon.png">
<link rel="icon" href="images/favicon.png">
<title><#Web_Title#> - Temperature</title>
<link rel="stylesheet" type="text/css" href="index_style.css">
<link rel="stylesheet" type="text/css" href="form_style.css">
<script type="text/javascript" src="/state.js"></script>
<script type="text/javascript" src="/general.js"></script>
<script type="text/javascript" src="/popup.js"></script>
<script type="text/javascript" src="/js/jquery.js"></script>
<script type="text/javascript">
var tempUnit = "C";

function initial(){
	show_menu();
	update_temp();
}

function format_temp(value){
	var n = parseFloat(value);
	if(isNaN(n) || n <= 0)
		return "disabled";
	if(tempUnit == "F")
		return Math.round(n * 9 / 5 + 32) + " °F";
	return Math.round(n) + " °C";
}

function render_temp(){
	document.getElementById("temp_24").innerHTML = format_temp(curr_coreTmp_2);
	document.getElementById("temp_5").innerHTML = format_temp(curr_coreTmp_5);
	document.getElementById("temp_cpu").innerHTML = format_temp(curr_cpuTemp);
}

function update_temp(){
	$.ajax({
		url: "/ajax_coretmp.asp",
		dataType: "script",
		cache: false,
		success: function(){
			render_temp();
			setTimeout(update_temp, 5000);
		},
		error: function(){
			setTimeout(update_temp, 5000);
		}
	});
}

function changeTempUnit(value){
	tempUnit = value;
	render_temp();
}
</script>
</head>
<body onload="initial();" class="bg">
<div id="TopBanner"></div>
<div id="Loading" class="popup_bg"></div>
<table class="content" align="center" cellpadding="0" cellspacing="0">
<tr>
	<td width="17">&nbsp;</td>
	<td valign="top" width="202">
		<div id="mainMenu"></div>
		<div id="subMenu"></div>
	</td>
	<td valign="top">
		<div id="tabMenu" class="submenuBlock"></div>
		<table width="98%" border="0" align="left" cellpadding="0" cellspacing="0">
		<tr>
			<td valign="top">
				<table width="760px" border="0" cellpadding="4" cellspacing="0" class="FormTitle" id="FormTitle">
				<tbody>
				<tr bgcolor="#4D595D">
					<td valign="top">
						<div>&nbsp;</div>
						<div class="formfonttitle"><#menu5_6#> - Temperature</div>
						<div style="margin:10px 0 10px 5px;" class="splitLine"></div>
						<table width="100%" border="1" align="center" cellpadding="4" cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
						<thead><tr><td colspan="2">Current temperatures</td></tr></thead>
						<tr><th>2.4 GHz radio</th><td><span id="temp_24">...</span></td></tr>
						<tr><th>5 GHz radio</th><td><span id="temp_5">...</span></td></tr>
						<tr><th>CPU</th><td><span id="temp_cpu">...</span></td></tr>
						<tr>
							<th>Temperature unit</th>
							<td>
								<select class="input_option" onchange="changeTempUnit(this.value);">
									<option value="C" selected>°C</option>
									<option value="F">°F</option>
								</select>
							</td>
						</tr>
						</table>
						<div style="margin-top:10px;color:#A7B5BC;">Values refresh every 5 seconds using the ASUS 52334 temperature endpoint.</div>
					</td>
				</tr>
				</tbody>
				</table>
			</td>
		</tr>
		</table>
	</td>
	<td width="10" align="center" valign="top">&nbsp;</td>
</tr>
</table>
<div id="footer"></div>
</body>
</html>
