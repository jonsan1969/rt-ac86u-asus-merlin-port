<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<html xmlns:v>
<head>
<meta http-equiv="X-UA-Compatible" content="IE=Edge"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta HTTP-EQUIV="Pragma" CONTENT="no-cache">
<meta HTTP-EQUIV="Expires" CONTENT="-1">
<title><#Web_Title#> - Other Settings</title>
<link rel="shortcut icon" href="images/favicon.png">
<link rel="icon" href="images/favicon.png">
<link rel="stylesheet" type="text/css" href="index_style.css">
<link rel="stylesheet" type="text/css" href="form_style.css">
<script type="text/javascript" src="/state.js"></script>
<script type="text/javascript" src="/general.js"></script>
<script type="text/javascript" src="/validator.js"></script>
<script type="text/javascript" src="/popup.js"></script>
<script type="text/javascript" src="/help.js"></script>
<script type="text/javascript" src="/js/jquery.js"></script>
<script>
<% login_state_hook(); %>

var tcp_defaults = [0, 2400, 120, 60, 120, 120, 10, 60, 30, 0];
var udp_defaults = [30, 180];

function parseTimeouts(value, expected, fallback) {
	var raw = value.replace(/^\s+|\s+$/g, "");
	if (raw == "")
		return fallback.slice(0);
	var parts = raw.split(/\s+/);
	if (parts.length != expected)
		return fallback.slice(0);
	for (var i = 0; i < parts.length; ++i) {
		if (!/^\d+$/.test(parts[i]))
			return fallback.slice(0);
		parts[i] = parseInt(parts[i], 10);
	}
	return parts;
}

function initial() {
	show_menu();
	show_footer();

	var tcp = parseTimeouts(document.form.ct_tcp_timeout.value, 10, tcp_defaults);
	var udp = parseTimeouts(document.form.ct_udp_timeout.value, 2, udp_defaults);

	document.getElementById("tcp_established").value = tcp[1];
	document.getElementById("tcp_syn_sent").value = tcp[2];
	document.getElementById("tcp_syn_recv").value = tcp[3];
	document.getElementById("tcp_fin_wait").value = tcp[4];
	document.getElementById("tcp_time_wait").value = tcp[5];
	document.getElementById("tcp_close").value = tcp[6];
	document.getElementById("tcp_close_wait").value = tcp[7];
	document.getElementById("tcp_last_ack").value = tcp[8];
	document.getElementById("udp_unreplied").value = udp[0];
	document.getElementById("udp_assured").value = udp[1];
}

function validRange(id, min, max) {
	return validator.numberRange(document.getElementById(id), min, max);
}

function applyRule() {
	if (!validRange("tcp_established", 1, 432000) ||
	    !validRange("tcp_syn_sent", 1, 86400) ||
	    !validRange("tcp_syn_recv", 1, 86400) ||
	    !validRange("tcp_fin_wait", 1, 86400) ||
	    !validRange("tcp_time_wait", 1, 86400) ||
	    !validRange("tcp_close", 1, 86400) ||
	    !validRange("tcp_close_wait", 1, 86400) ||
	    !validRange("tcp_last_ack", 1, 86400) ||
	    !validRange("udp_assured", 1, 86400) ||
	    !validRange("udp_unreplied", 1, 86400))
		return false;

	document.form.ct_tcp_timeout.value = "0 " +
		document.getElementById("tcp_established").value + " " +
		document.getElementById("tcp_syn_sent").value + " " +
		document.getElementById("tcp_syn_recv").value + " " +
		document.getElementById("tcp_fin_wait").value + " " +
		document.getElementById("tcp_time_wait").value + " " +
		document.getElementById("tcp_close").value + " " +
		document.getElementById("tcp_close_wait").value + " " +
		document.getElementById("tcp_last_ack").value + " 0";
	document.form.ct_udp_timeout.value =
		document.getElementById("udp_unreplied").value + " " +
		document.getElementById("udp_assured").value;

	showLoading();
	document.form.submit();
	return true;
}
</script>
</head>

<body onload="initial();" onunload="unload_body();">
<div id="TopBanner"></div>
<div id="Loading" class="popup_bg"></div>

<iframe name="hidden_frame" id="hidden_frame" src="" width="0" height="0" frameborder="0"></iframe>

<form method="post" name="form" action="/start_apply.htm" target="hidden_frame">
<input type="hidden" name="current_page" value="Tools_OtherSettings.asp">
<input type="hidden" name="next_page" value="Tools_OtherSettings.asp">
<input type="hidden" name="modified" value="0">
<input type="hidden" name="action_mode" value="apply">
<input type="hidden" name="action_script" value="restart_conntrack">
<input type="hidden" name="action_wait" value="5">
<input type="hidden" name="first_time" value="">
<input type="hidden" name="preferred_lang" value="<% nvram_get("preferred_lang"); %>">
<input type="hidden" name="firmver" value="<% nvram_get("firmver"); %>">
<input type="hidden" name="ct_tcp_timeout" value="<% nvram_get("ct_tcp_timeout"); %>">
<input type="hidden" name="ct_udp_timeout" value="<% nvram_get("ct_udp_timeout"); %>">

<table class="content" align="center" cellpadding="0" cellspacing="0">
<tr>
<td width="17">&nbsp;</td>
<td valign="top" width="202"><div id="mainMenu"></div><div id="subMenu"></div></td>
<td valign="top">
<div id="tabMenu" class="submenuBlock"></div>
<table width="98%" border="0" align="left" cellpadding="0" cellspacing="0">
<tr><td valign="top">
<table width="100%" border="0" cellpadding="5" cellspacing="0" class="FormTitle">
<tr><td bgcolor="#4D595D" valign="top">
<div>&nbsp;</div>
<div class="formfonttitle">Tools - Other Settings</div>
<div style="margin:10px 0 10px 5px;" class="splitLine"></div>
<div class="formfontdesc">
Conntrack timeout tuning using the ASUS 52334 backend. Only settings verified in the stock RT-AC86U runtime are exposed here.
</div>

<table width="100%" border="1" align="center" cellpadding="4" cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
<thead><tr><td colspan="2">TCP/IP settings</td></tr></thead>
<tr><th>TCP Timeout: Established</th><td><input id="tcp_established" type="text" maxlength="6" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: SYN sent</th><td><input id="tcp_syn_sent" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: SYN received</th><td><input id="tcp_syn_recv" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: FIN wait</th><td><input id="tcp_fin_wait" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: TIME wait</th><td><input id="tcp_time_wait" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: Close</th><td><input id="tcp_close" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: Close wait</th><td><input id="tcp_close_wait" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>TCP Timeout: Last ACK</th><td><input id="tcp_last_ack" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>UDP Timeout: Assured</th><td><input id="udp_assured" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
<tr><th>UDP Timeout: Unreplied</th><td><input id="udp_unreplied" type="text" maxlength="5" class="input_6_table" onkeypress="return validator.isNumber(this,event);"></td></tr>
</table>

<div class="apply_gen"><input class="button_gen" onclick="applyRule();" type="button" value="<#CTL_apply#>"></div>
</td></tr>
</table>
</td></tr>
</table>
</td>
<td width="10" align="center" valign="top">&nbsp;</td>
</tr>
</table>
</form>
<div id="footer"></div>
</body>
</html>
