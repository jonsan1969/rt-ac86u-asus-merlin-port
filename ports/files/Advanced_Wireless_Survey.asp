<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=Edge" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<meta HTTP-EQUIV="Pragma" CONTENT="no-cache">
<meta HTTP-EQUIV="Expires" CONTENT="-1">
<link rel="shortcut icon" href="images/favicon.png">
<link rel="icon" href="images/favicon.png">
<title><#Web_Title#> - Site Survey</title>
<link rel="stylesheet" type="text/css" href="/form_style.css">
<link rel="stylesheet" type="text/css" href="/index_style.css">
<script type="text/javascript" src="/state.js"></script>
<script type="text/javascript" src="/general.js"></script>
<script type="text/javascript" src="/popup.js"></script>
<script type="text/javascript" src="/js/jquery.js"></script>
<style type="text/css">
.survey_table{width:100%;border-collapse:collapse;background:#2B373B;color:#fff;font-size:12px;}
.survey_table th{height:30px;border:1px solid #334044;background:#151E21;text-align:left;padding:4px;}
.survey_table td{border:1px solid #334044;color:#A7C1CB;padding:5px;}
.survey_center{text-align:center !important;}
.survey_signal{font-weight:bold;color:#FC0;}
</style>
<script type="text/javascript">
var aplist = [];
var wlc_scan_state = "0";
var pollCount = 0;
var maxPolls = 60;

function safeText(value){
	if(value === null || typeof(value) === "undefined")
		return "";
	return String(value)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#39;");
}

function decodeSsid(value){
	try{
		return decodeURIComponent(value || "");
	}
	catch(e){
		return value || "";
	}
}

function initial(){
	show_menu();
	refreshSurvey(false);
}

function startScan(){
	document.getElementById("rescanButton").disabled = true;
	document.getElementById("scanStatus").innerHTML = "Scanning...";
	document.form.flag.value = "sitesurvey";
	document.form.action_script.value = "restart_wlcscan";
	document.form.submit();
	pollCount = 0;
	setTimeout(function(){ refreshSurvey(true); }, 1000);
}

function refreshSurvey(scanning){
	$.ajax({
		url: "/apscan.asp",
		dataType: "script",
		cache: false,
		success: function(){
			renderSurvey();
			if(wlc_scan_state == "5"){
				document.getElementById("rescanButton").disabled = false;
				document.getElementById("scanStatus").innerHTML = "Scan complete";
				return;
			}
			if(!scanning && pollCount == 0){
				startScan();
				return;
			}
			pollCount++;
			if(pollCount < maxPolls){
				document.getElementById("scanStatus").innerHTML = "Scanning...";
				setTimeout(function(){ refreshSurvey(true); }, 2000);
			}
			else{
				document.getElementById("rescanButton").disabled = false;
				document.getElementById("scanStatus").innerHTML = "Scan timed out";
			}
		},
		error: function(){
			pollCount++;
			if(pollCount < maxPolls)
				setTimeout(function(){ refreshSurvey(true); }, 2000);
			else{
				document.getElementById("rescanButton").disabled = false;
				document.getElementById("scanStatus").innerHTML = "Unable to read scan results";
			}
		}
	});
}

function renderSurvey(){
	var rows = [];
	var list = (aplist && aplist.length) ? aplist.slice(0) : [];
	list.sort(function(a,b){ return parseInt(b[5],10) - parseInt(a[5],10); });

	rows.push('<table class="survey_table">');
	rows.push('<tr><th>SSID</th><th class="survey_center">Channel</th><th>Security</th><th class="survey_center">Band</th><th class="survey_center">Signal</th><th>BSSID</th></tr>');
	if(!list.length){
		rows.push('<tr><td colspan="6" class="survey_center">No networks reported yet.</td></tr>');
	}
	else{
		for(var i=0;i<list.length;i++){
			var ap = list[i];
			if(!ap || ap[1] === null || String(ap[1]).indexOf("%FFFF") !== -1)
				continue;
			var security = (ap[3] || "");
			if(ap[4] && ap[4] !== "NONE")
				security += " (" + ap[4] + ")";
			var band = (ap[0] == "2G") ? "2.4 GHz" : "5 GHz";
			rows.push("<tr>");
			rows.push("<td>" + safeText(decodeSsid(ap[1])) + "</td>");
			rows.push('<td class="survey_center">' + safeText(ap[2]) + (ap[7] ? " (" + safeText(ap[7]) + ")" : "") + "</td>");
			rows.push("<td>" + safeText(security) + "</td>");
			rows.push('<td class="survey_center">' + safeText(band) + "</td>");
			rows.push('<td class="survey_center survey_signal">' + safeText(ap[5]) + "%</td>");
			rows.push("<td>" + safeText(ap[6]) + "</td>");
			rows.push("</tr>");
		}
	}
	rows.push("</table>");
	document.getElementById("surveyResults").innerHTML = rows.join("");
}
</script>
</head>
<body onload="initial();" class="bg">
<div id="TopBanner"></div>
<div id="Loading" class="popup_bg"></div>
<iframe name="hidden_frame" id="hidden_frame" src="" width="0" height="0" frameborder="0"></iframe>
<form method="post" name="form" action="/start_apply2.htm" target="hidden_frame">
<input type="hidden" name="current_page" value="Advanced_Wireless_Survey.asp">
<input type="hidden" name="next_page" value="Advanced_Wireless_Survey.asp">
<input type="hidden" name="prev_page" value="Advanced_Wireless_Survey.asp">
<input type="hidden" name="modified" value="0">
<input type="hidden" name="flag" value="sitesurvey">
<input type="hidden" name="action_mode" value="apply">
<input type="hidden" name="action_wait" value="1">
<input type="hidden" name="action_script" value="restart_wlcscan">
<input type="hidden" name="first_time" value="">
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
						<div class="formfonttitle">Wireless - Visible Networks</div>
						<div style="margin:10px 0 10px 5px;" class="splitLine"></div>
						<div class="apply_gen">
							<input type="button" id="rescanButton" value="Rescan" onclick="startScan();" class="button_gen" />
							<span id="scanStatus" style="margin-left:10px;color:#FC0;"></span>
						</div>
						<div id="surveyResults" style="margin:10px 0 0 5px;width:735px;"></div>
					</td>
				</tr>
				</tbody>
				</table>
			</td>
		</tr>
		</table>
	</td>
	<td width="10">&nbsp;</td>
</tr>
</table>
</form>
<div id="footer"></div>
</body>
</html>
