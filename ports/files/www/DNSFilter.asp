<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="X-UA-Compatible" content="IE=Edge"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta HTTP-EQUIV="Pragma" CONTENT="no-cache">
<meta HTTP-EQUIV="Expires" CONTENT="-1">
<title><#Web_Title#>DNS Director</title>
<link rel="shortcut icon" href="images/favicon.png">
<link rel="icon" href="images/favicon.png">
<link rel="stylesheet" type="text/css" href="ParentalControl.css">
<link rel="stylesheet" type="text/css" href="index_style.css">
<link rel="stylesheet" type="text/css" href="form_style.css">
<link rel="stylesheet" type="text/css" href="usp_style.css">
<script type="text/javascript" src="/state.js"></script>
<script type="text/javascript" src="/popup.js"></script>
<script type="text/javascript" src="/help.js"></script>
<script type="text/javascript" src="/general.js"></script>
<script type="text/javascript" src="/client_function.js"></script>
<script type="text/javascript" src="/js/jquery.js"></script>
<script type="text/javascript" src="/validator.js"></script>
<script type="text/javascript">

<% login_state_hook(); %>

/*
 * RT-AC86U 386_52334 compatibility adapter.
 *
 * ASUS 52334 retains the DNSFilter backend but only exposes one
 * dnsfilter_rulelist NVRAM field and IPv4 custom DNS entries.
 * Do not add Merlin-only rulelist1..5 or dnsfilter_custom61..63 here.
 */
var dnsfilter_rule_list = '<% nvram_get("dnsfilter_rulelist"); %>'
	.replace(/&#60;?/g, "<")
	.replace(/&#62;?/g, ">");

/* Ask the ASUS 52334 httpd backend which modes it implements. */
var backend_modes = <% dnsfilter_modes_list(); %>;
var hidden_modes = {"2": true, "3": true, "4": true};

function modeLabel(value, fallback){
	var labels = {
		"0": "No Redirection",
		"8": "User Defined 1",
		"9": "User Defined 2",
		"10": "User Defined 3",
		"11": "Router",
		"17": "Cloudflare Safe",
		"18": "Cloudflare Family",
		"19": "AdGuard Ad block",
		"20": "AdGuard Family"
	};
	return labels[value] || fallback;
}

function availableModes(){
	var out = [];
	for(var i = 0; i < backend_modes.length; ++i){
		var value = String(backend_modes[i][0]);
		if(hidden_modes[value])
			continue;
		out.push([value, modeLabel(value, backend_modes[i][1])]);
	}
	return out;
}

function htmlEscape(s){
	return String(s)
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#39;");
}

function validIPv4(value){
	if(value == "")
		return true;
	var parts = value.split(".");
	if(parts.length != 4)
		return false;
	for(var i = 0; i < 4; ++i){
		if(!/^\d{1,3}$/.test(parts[i]))
			return false;
		var n = parseInt(parts[i], 10);
		if(n < 0 || n > 255)
			return false;
	}
	return true;
}

function validMac(value){
	return /^([0-9A-F]{2}:){5}[0-9A-F]{2}$/.test(value);
}

function fillModeSelect(obj, selected){
	var modes = availableModes();
	obj.options.length = 0;
	for(var i = 0; i < modes.length; ++i){
		var opt = new Option(modes[i][1], modes[i][0]);
		if(String(selected) == modes[i][0])
			opt.selected = true;
		obj.options.add(opt);
	}
}

function parseRules(){
	var rows = [];
	var parts = dnsfilter_rule_list.split("<");
	for(var i = 1; i < parts.length; ++i){
		if(!parts[i])
			continue;
		var fields = parts[i].split(">");
		if(fields.length < 3)
			continue;
		var mac = String(fields[1] || "").toUpperCase();
		var mode = String(fields[2] || "0");
		if(validMac(mac))
			rows.push({mac: mac, mode: mode});
	}
	return rows;
}

function rebuildRules(rows){
	var value = "";
	for(var i = 0; i < rows.length; ++i)
		value += "<>" + rows[i].mac + ">" + rows[i].mode;
	return value;
}

function clientName(mac){
	try {
		if(typeof clientList != "undefined" && clientList[mac]){
			if(clientList[mac].nickName)
				return clientList[mac].nickName;
			if(clientList[mac].name)
				return clientList[mac].name;
		}
	} catch(e) {}
	return mac;
}

function show_dnsfilter_list(){
	var rows = parseRules();
	var code = '<table width="100%" border="1" cellspacing="0" cellpadding="4" align="center" class="list_table">';
	if(rows.length == 0){
		code += '<tr><td class="hint-color" colspan="3"><#IPConnection_VSList_Norule#></td></tr>';
	}
	else {
		for(var i = 0; i < rows.length; ++i){
			code += '<tr>';
			code += '<td width="50%"><div>' + htmlEscape(clientName(rows[i].mac)) + '</div><div>' + rows[i].mac + '</div></td>';
			code += '<td width="35%"><select class="input_option" id="rule_mode_' + i + '" onchange="changeRuleMode(' + i + ', this.value)"></select></td>';
			code += '<td width="15%"><input class="remove_btn" onclick="deleteRule(' + i + ');" value=""/></td>';
			code += '</tr>';
		}
	}
	code += '</table>';
	document.getElementById("mainTable_Block").innerHTML = code;

	for(var j = 0; j < rows.length; ++j)
		fillModeSelect(document.getElementById("rule_mode_" + j), rows[j].mode);

	document.getElementById("storage_usage").innerHTML =
		dnsfilter_rule_list.length + " / 255 bytes";
}

function setclientmac(macaddr){
	document.form.rule_mac.value = String(macaddr).toUpperCase();
	hideClients_Block();
}

function pullLANIPList(obj){
	var element = document.getElementById("ClientList_Block_PC");
	var open = element.offsetWidth > 0 || element.offsetHeight > 0;
	if(!open){
		obj.src = "/images/arrow-top.gif";
		element.style.display = "block";
		document.form.rule_mac.focus();
	}
	else
		hideClients_Block();
}

function hideClients_Block(){
	document.getElementById("pull_arrow").src = "/images/arrow-down.gif";
	document.getElementById("ClientList_Block_PC").style.display = "none";
}

function addRule(){
	var mac = document.form.rule_mac.value.toUpperCase().replace(/\s/g, "");
	var mode = document.form.rule_mode.value;
	if(!validMac(mac)){
		alert("Enter a valid MAC address.");
		document.form.rule_mac.focus();
		return false;
	}

	var rows = parseRules();
	for(var i = 0; i < rows.length; ++i){
		if(rows[i].mac == mac){
			alert("This client already has a DNS Director rule.");
			return false;
		}
	}

	rows.push({mac: mac, mode: mode});
	var candidate = rebuildRules(rows);
	if(candidate.length > 255){
		alert("ASUS 386_52334 stores DNSFilter client rules in one 255-byte NVRAM field. Remove an existing rule before adding another.");
		return false;
	}

	dnsfilter_rule_list = candidate;
	document.form.rule_mac.value = "";
	show_dnsfilter_list();
	return true;
}

function deleteRule(index){
	var rows = parseRules();
	rows.splice(index, 1);
	dnsfilter_rule_list = rebuildRules(rows);
	show_dnsfilter_list();
}

function changeRuleMode(index, value){
	var rows = parseRules();
	if(index < 0 || index >= rows.length)
		return;
	rows[index].mode = value;
	dnsfilter_rule_list = rebuildRules(rows);
	show_dnsfilter_list();
}

function updateVisibility(){
	var enabled = (document.form.dnsfilter_enable_x.value == "1");
	showhide("dnsfilter_settings", enabled);
	showhide("client_rules", enabled);
}

function applyRule(){
	var custom = [
		document.form.dnsfilter_custom1.value,
		document.form.dnsfilter_custom2.value,
		document.form.dnsfilter_custom3.value
	];
	for(var i = 0; i < custom.length; ++i){
		if(!validIPv4(custom[i])){
			alert("User Defined DNS " + (i + 1) + " is not a valid IPv4 address.");
			return false;
		}
	}

	if(dnsfilter_rule_list.length > 255){
		alert("The DNSFilter rule list exceeds the ASUS 52334 storage limit.");
		return false;
	}

	document.form.dnsfilter_rulelist.value = dnsfilter_rule_list;
	showLoading();
	document.form.submit();
	return true;
}

function initial(){
	show_menu();
	show_footer();

	document.form.dnsfilter_enable_x.value = '<% nvram_get("dnsfilter_enable_x"); %>' || "0";
	fillModeSelect(document.form.dnsfilter_mode, '<% nvram_get("dnsfilter_mode"); %>');
	fillModeSelect(document.form.rule_mode, "0");
	show_dnsfilter_list();
	updateVisibility();

	try {
		showDropdownClientList("setclientmac", "mac", "all", "ClientList_Block_PC", "pull_arrow", "all");
	} catch(e) {}
}

</script>
</head>

<body onload="initial();" onunload="unload_body();" class="bg">
<div id="TopBanner"></div>
<div id="Loading" class="popup_bg"></div>

<iframe name="hidden_frame" id="hidden_frame" width="0" height="0" frameborder="0"></iframe>
<form method="post" name="form" action="/start_apply.htm" target="hidden_frame">
<input type="hidden" name="productid" value="<% nvram_get("productid"); %>">
<input type="hidden" name="current_page" value="DNSFilter.asp">
<input type="hidden" name="next_page" value="">
<input type="hidden" name="modified" value="0">
<input type="hidden" name="action_wait" value="5">
<input type="hidden" name="action_mode" value="apply">
<input type="hidden" name="action_script" value="restart_dnsfilter">
<input type="hidden" name="preferred_lang" value="<% nvram_get("preferred_lang"); %>">
<input type="hidden" name="firmver" value="<% nvram_get("firmver"); %>">
<input type="hidden" name="dnsfilter_rulelist" value="">

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
		<tr><td valign="top">
			<table width="730px" border="0" cellpadding="4" cellspacing="0" class="FormTitle">
			<tbody><tr><td bgcolor="#4D595D" valign="top">
				<div>&nbsp;</div>
				<div class="formfonttitle">DNS Director</div>
				<div style="margin:10px 0 10px 5px;" class="splitLine"></div>
				<div class="formfontdesc">
					Force LAN clients to selected DNS resolvers using the DNSFilter backend retained in ASUS RT-AC86U 386_52334.
					This compatibility port intentionally uses only the stock 52334 storage format: IPv4 custom resolvers and one 255-byte client-rule list.
				</div>

				<table width="100%" border="1" align="center" cellpadding="4" cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
				<thead><tr><td colspan="2">Settings</td></tr></thead>
				<tr>
					<th>Enable DNS Director</th>
					<td>
						<select class="input_option" name="dnsfilter_enable_x" onchange="updateVisibility();">
							<option value="0">No</option>
							<option value="1">Yes</option>
						</select>
					</td>
				</tr>
				<tbody id="dnsfilter_settings">
				<tr>
					<th>Global Redirection</th>
					<td><select name="dnsfilter_mode" class="input_option"></select></td>
				</tr>
				<tr>
					<th>User Defined DNS 1</th>
					<td><input type="text" maxlength="15" class="input_15_table" name="dnsfilter_custom1" value="<% nvram_get("dnsfilter_custom1"); %>" onKeyPress="return validator.isIPAddr(this,event)"></td>
				</tr>
				<tr>
					<th>User Defined DNS 2</th>
					<td><input type="text" maxlength="15" class="input_15_table" name="dnsfilter_custom2" value="<% nvram_get("dnsfilter_custom2"); %>" onKeyPress="return validator.isIPAddr(this,event)"></td>
				</tr>
				<tr>
					<th>User Defined DNS 3</th>
					<td><input type="text" maxlength="15" class="input_15_table" name="dnsfilter_custom3" value="<% nvram_get("dnsfilter_custom3"); %>" onKeyPress="return validator.isIPAddr(this,event)"></td>
				</tr>
				</tbody>
				</table>

				<div id="client_rules">
				<table width="100%" border="1" cellspacing="0" cellpadding="4" align="center" class="FormTable_table" style="margin-top:8px;">
				<thead><tr><td colspan="3">Client rules <span id="storage_usage" style="float:right;"></span></td></tr></thead>
				<tr>
					<th>Client MAC address</th>
					<th>Redirection</th>
					<th><#list_add_delete#></th>
				</tr>
				<tr>
					<td width="50%">
						<input type="text" maxlength="17" style="margin-left:10px;width:255px;" autocorrect="off" autocapitalize="off" class="input_macaddr_table" name="rule_mac" onClick="hideClients_Block();" placeholder="AA:BB:CC:DD:EE:FF">
						<img id="pull_arrow" height="14px" src="/images/arrow-down.gif" style="position:absolute;" onclick="pullLANIPList(this);" title="<#select_client#>">
						<div id="ClientList_Block_PC" style="margin:0 0 0 52px" class="clientlist_dropdown"></div>
					</td>
					<td width="35%"><select class="input_option" name="rule_mode"></select></td>
					<td width="15%"><input class="add_btn" type="button" onclick="addRule();" value=""></td>
				</tr>
				</table>

				<div id="mainTable_Block"></div>
				</div>

				<div class="apply_gen">
					<input type="button" class="button_gen" onclick="applyRule();" value="<#CTL_apply#>"/>
				</div>
			</td></tr></tbody>
			</table>
		</td></tr>
		</table>
	</td>
	<td width="10" align="center" valign="top">&nbsp;</td>
</tr>
</table>

<div id="footer"></div>
</form>
</body>
</html>
