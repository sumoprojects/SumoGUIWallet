#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
Main UI html
'''

html ="""
<!DOCTYPE html>
<html>
    <head>
        <link href="./css/bootstrap.min.css" rel="stylesheet">
        <link href="./css/font-awesome.min.css" rel="stylesheet">
        <style type="text/css">
            * {
                -webkit-box-sizing: border-box;
                -moz-box-sizing: border-box;
                box-sizing: border-box;
            }
            
            body {
                -webkit-user-select: none;
                user-select: none;
              
                cursor: default;
                background-color: #fff;
                color: #76A500;
                background-position: center center;
                font-family: "RoboReg", "Helvetica Neue",Helvetica,Arial,sans-serif;
                font-size: 14px;
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            
            a, a:hover, a:active, a:focus {
                text-decoration: none;
                outline: 0;
                cursor: default;
            }
            
            a, a:active, a:focus{
                color: #337AB7;
            }
            
            a:hover{
                color: #fff;
            }
            
            .nav-tabs{
                /*width: 760px;*/
            }
            .nav-tabs li{
                width: 20%;
                text-align: center;
                font-size: 120%
            }
            
            .container{
                width: 760px;
                padding: 0;
                margin: 5px 0px 5px 20px;
            }
            
            h3{
                text-align: center;
                margin-bottom: 1em;
                font-size: 180%;
            }
                       
                        
            .tab-content{
                font-size: 12px;
            }
            
            .tab-content h3{
                margin-top: 0;
            }
            
            #balance_tab h4, #balance_tab h5{
                color: #76A500;
            }
            
            #balance_tab h5 span{
                color: #ccc;
            }
            
            #settings_tab h3{
                margin-top: 20px;
                margin-bottom: 30px;
            }
            
            .syncing{
                font-size: 60%;
            }
            
            .tab-content .tab-pane {    
                position: relative;
            }
            
            .form-horizontal .control-label{
                text-align: left;
            }
                       
            
            .progress{
                height: 22px;
                text-align: center;
                background: #ddd;
            }
            
            #progress_bar_text_high{
                font-size: 90%; 
                display: none;
            }
            
            #progress_bar_text_low{
                font-size: 80%;
                color: #c7254e;
            }
            
            .control-label{
                font-weight: bold;
            }
            
            .tx-list{
                color: #666;
                margin-right: 20px;
                font-weight: bold;
            }
            
            .tx-list a{
                cursor: pointer;
            }
            
            .tx-list.tx-out, .tx-list.tx-in, .tx-list.tx-pool, .tx-list.tx-pending, .tx-list.tx-out a, .tx-list.tx-out a:active, .tx-list.tx-out a:focus{
                color: #c7254e;
                margin-bottom: 0;
            }
            
            .tx-list.tx-in, .tx-list.tx-in a, .tx-list.tx-in a:active, .tx-list.tx-in a:focus{
                color: green;
            }
            
            .tx-list.tx-pool, .tx-list.tx-pending, .tx-list.tx-pending a, .tx-list.tx-pending a:active, .tx-list.tx-pending a:focus, .tx-list.tx-pool a, .tx-list.tx-pool a:active, .tx-list.tx-pool a:focus{
                color: orange;
            }
            
            .tx-list a:hover{
                color: #337AB7;
            }
            
            .tx-list.txid{
                color: inherit;
            }
            
            .tx-list.tx-payment-id{
                font-weight: normal;
            }
            
            .tx-fee-hide, .tx-note-hide, .tx-destinations-hide{
                display: none;
            }
            
            .tx-list.tx-lock{
                color: #666;
            }
            
            .modal-progress-text{
                color: #333;
                font-size: 90%;
                font-weight: bold;
                margin-left: 10px;
            }
            
            #form_receive input, #form_send_tx input, #form_send_tx select{
                font-size: 14px;
            }
            
            .btn-sm{
                border-radius: 0;
            }
            
            table {
                border-spacing: 0;
                border-collapse: collapse;
                font-size: 12px;
            }
            
            table thead tr{
                height: 3em;
            }
            
            table tbody tr {
                color: #aaa;
                height: 3em;
                line-height: 1.6em;
            }
            
            table thead tr th{
                text-align: left;
                text-size: 18px;
                padding: auto 1em;
            }
            
            table tbody tr td a:hover{
                color: #666;
                cursor: pointer;
            }
            
            .address-book-row{
                cursor: pointer;
            }
            
            #address-book-box{
                max-height: 450px;
            }
            
            #address-book-box table{
                width: 100%;
            }
            
            #address-book-box table thead {
                display: inline-block;
                width: 100%;
            }
            
            #address-book-box table tbody {
                border-top: none;
                max-height: 300px;
                display: inline-block;
                width: 100%;
                overflow: auto;
            }
            
            #address-book-box table tbody::-webkit-scrollbar-track,
                .tx-destinations::-webkit-scrollbar-track
            {
                -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
                background-color: #F5F5F5;
                border-radius: 6px;
            }
                       
            
            #address-book-box table tbody::-webkit-scrollbar,
                .tx-destinations::-webkit-scrollbar
            {
                width: 8px;
                background-color: #F5F5F5;
                border-radius: 6px;
            }
            
            .tx-destinations::-webkit-scrollbar{
                height: 8px;
            }
            
            #address-book-box table tbody::-webkit-scrollbar-thumb,
                .tx-destinations::-webkit-scrollbar-thumb
            {
                border-radius: 6px;
                -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
                background-color: #5BB0F7;
            }
            
            .tx-destinations {
                width: 100%;
                max-height: 200px;
                overflow: auto;
                font-size: 90%;
            }
            
            .wallet-settings{
                text-align: center;
            }
            
            .wallet-settings button{
                margin-left: 20px;
            }
            
            .form-control.address-box{
                font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
                font-size: 85%;
                color: #000;
            }
            
            textarea{
                border:none;
                width:100%;
                resize:none;
                font-weight:bold;
            }
            
            .panel-default>.panel-heading {
              color: #666;
              background-color: #eee;
              border-color: #e4e5e7;
              padding: 0;
              -webkit-user-select: none;
              -moz-user-select: none;
              -ms-user-select: none;
              user-select: none;
            }
            
            .panel-default>.panel-heading a {
              display: block;
              padding: 10px 15px;
            }
            
            .panel-default>.panel-heading a:after {
              font-family:'Glyphicons Halflings';
              content: "";
              position: relative;
              top: 1px;
              display: inline-block;
              font-style: normal;
              font-weight: 400;
              line-height: 1;
              -webkit-font-smoothing: antialiased;
              -moz-osx-font-smoothing: grayscale;
              float: right;
              transition: transform .25s linear;
              -webkit-transition: -webkit-transform .25s linear;
            }
            
            .panel-default>.panel-heading a[aria-expanded="true"] {
              background-color: #2196F3;
              color: #fff;
              font-weight: bold;
            }
            
            .panel-default>.panel-heading a[aria-expanded="false"] {
                color: #666;
            }
            
            .panel-default>.panel-heading a[aria-expanded="true"]:after {
              content:"\e114";
              
            }
            
            .panel-default>.panel-heading a[aria-expanded="false"]:after {
              content:"\e080";
            }
            
            .panel-default > .panel-heading + .panel-collapse > .panel-body {
                height: 295px;
                overflow: auto;
            }
            
            
            .panel-default > .panel-heading + .panel-collapse > .panel-body::-webkit-scrollbar-track
            {
                -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
                border-radius: 6px;
                background-color: #F5F5F5;
            }
                       
            
            .panel-default > .panel-heading + .panel-collapse > .panel-body::-webkit-scrollbar
            {
                width: 8px;
                background-color: #F5F5F5;
            }
                        
            .panel-default > .panel-heading + .panel-collapse > .panel-body::-webkit-scrollbar-thumb
            {
                border-radius: 6px;
                -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.3);
                background-color: #5BB0F7;
            }
            
        </style>
        
        <script src="./scripts/jquery-1.9.1.min.js"></script>
        <script src="./scripts/bootstrap.min.js"></script>
        <script src="./scripts/mustache.min.js"></script>
        <script src="./scripts/jquery.qrcode.min.js"></script>
        <script src="./scripts/utils.js"></script>
        <script type="text/javascript">
                                   
            function app_ready(){
                setTimeout(app_hub.load_app_settings, 2000);
                app_hub.on_load_app_settings_completed_event.connect(function(app_settings_json){
                    var app_settings = $.parseJSON(app_settings_json);
                    var log_level = app_settings['daemon']['log_level'];
                    $('#daemon_log_level_' + log_level).prop('checked', true);
                    var block_sync_size = app_settings['daemon']['block_sync_size'];
                    $('#block_sync_size_' + block_sync_size).prop('checked', true);
                });
                
                app_hub.on_main_wallet_ui_reset_event.connect(function(){
                    setTimeout(function(){
                        location.reload();
                    }, 5000);
                });
                                
                app_hub.on_daemon_update_status_event.connect(update_daemon_status);
                app_hub.on_wallet_update_info_event.connect(update_wallet_info);
                app_hub.on_wallet_rescan_spent_completed_event.connect(function(){
                    rescan_spent_btn.disable(false);
                    rescan_bc_btn.disable(false);
                    hide_progress();
                });
                
                app_hub.on_wallet_rescan_bc_completed_event.connect(function(){
                    rescan_spent_btn.disable(false);
                    rescan_bc_btn.disable(false);
                    hide_progress();
                });
                
                app_hub.on_wallet_send_tx_completed_event.connect(function(status_json){
                    var status = $.parseJSON(status_json);
                    if(status['status'] == "OK"){
                        $("#form_send_tx")[0].reset();
                    }
                    else{
                        if(status['message'].search("Invalid address format") >= 0){
                            $('#send_address').parent().addClass('has-error');
                        }
                        else if(status['message'].search("Payment id has invalid format") >= 0){
                            $('#send_payment_id').parent().addClass('has-error');
                        }
                        else if(status['message'].search("not enough money") >= 0){
                            $('#send_amount').parent().addClass('has-error');
                        }
                    }
                    
                    btn_send_tx.disable(false);
                    hide_progress();
                });
                
                app_hub.on_generate_payment_id_event.connect(function(payment_id, integrated_address){
                    $('#receive_payment_id').val(payment_id);
                    receive_integrated_address.val(integrated_address);
                    $('#receive_address_qrcode').html("");
                    $('#receive_address_qrcode').qrcode({width: 220,height: 220, text: integrated_address});
                    $('#btn_copy_integrated_address').disable(false);
                    hide_progress();
                });
                
                app_hub.on_load_address_book_completed_event.connect(function(address_book){
                    address_book = $.parseJSON(address_book);
                    hide_progress();
                    var html = "Address book empty!";
                    if(address_book.length > 0){
                        html = '<div id="address-book-box" class="table-responsive">'; 
                        html += '<table class="table table-hover table-condensed"><thead><tr><th width="160px" style="border:none">Address</th><th width="150px" style="border:none">Payment ID</th><th width="200px" style="border:none">Description</th><th width="50px" style="border:none">&nbsp;</th></tr></thead><tbody>';
                        var row_tmpl = $('#address_book_row_templ').html();
                        for(var i=0; i<address_book.length; i++){
                            var entry = address_book[i];
                            var address = entry['address'];
                            var payment_id = entry['payment_id'];
                            if(payment_id.substring(16) == "000000000000000000000000000000000000000000000000"){
                                payment_id = payment_id.substring(0, 16);
                            }
                            if(payment_id == "0000000000000000"){
                                payment_id = "";
                            }
                            
                            var payment_id_short = payment_id.length > 16 ? payment_id.substring(0,18) + '...' : payment_id;
                            var address_short = address.substring(0,18) + '...';
                            var desc_short = entry['description'].length > 50 ? entry['description'].substring(0, 50) + '...' : entry['description'];
                            
                            var row_html = Mustache.render(row_tmpl, 
                                                                    {   
                                                                        'address': address,
                                                                        'payment_id': payment_id,
                                                                        'address_short': address_short,
                                                                        'payment_id_short': payment_id_short,
                                                                        'desc_short': desc_short,
                                                                        'index': entry['index']
                                                                    });
                            
                            html += row_html;
                        }
                        html += "</tbody></table></div>";
                    }
                    
                    show_app_dialog(html);
                    
                    $(".address-book-row").click(function() {
                        $("#send_address").val( $(this).data("address") );
                        $("#send_payment_id").val( $(this).data("payment-id") );
                        hide_app_dialog();
                        return false;
                    });
                });
                
                app_hub.on_tx_detail_found_event.connect(function(tx_detail_json){
                    var tx = $.parseJSON(tx_detail_json);
                    if(tx['status'] == "ERROR"){
                        hide_progress();
                        return;
                    }
                    
                    var tx_status_text = tx['status'] == "in" || tx['status'] == "out" ? "Completed" :  (tx['status'] == "pending" ? "Pending" : "In Pool");
                    if(tx['confirmation'] < 10){
                        if(tx_status_text == "Completed") tx_status_text = "Locked";
                        tx_status_text += " (+" + tx['confirmation'] + " confirms)";                
                    }
                    
                    var dest_html = "";
                    if(tx.hasOwnProperty('destinations')){
                        var destinations = tx['destinations'];
                        for(var i=0; i < destinations.length; i++ ){
                            dest_html += '<li>Amount: <span class="tx-list tx-amount tx-' + tx['status'] + '">' + printMoney(destinations[i]['amount']/1000000000) + "</span>Address: <strong>" + destinations[i]['address'] + "</strong></li>";
                        }
                    }
                    
                    
                    var tx_row_tmpl = $('#tx_detail_templ').html();
                    var tx_rendered = Mustache.render(tx_row_tmpl, 
                                                        {   'cls_in_out': tx['status'],
                                                            'tx_direction': tx['direction'] == "in" ? "Incoming Tx:" : "Outgoing Tx:",
                                                            'tx_status': tx_status_text,
                                                            'tx_fa_icon': tx['direction'] == "in" ? "mail-forward" : "reply",
                                                            'tx_id': tx['txid'],
                                                            'tx_payment_id': tx['payment_id'], 
                                                            'tx_amount': printMoney(tx['amount']/1000000000.),
                                                            'tx_fee': printMoney(tx['fee']/1000000000.),
                                                            'tx_fee_hide': tx['fee'] > 0 ? '' : 'tx-fee-hide',
                                                            'tx_date': dateConverter(tx['timestamp']),
                                                            'tx_time': timeConverter(tx['timestamp']),
                                                            'tx_height': tx['height'] > 0 ? tx['height'] : "?" ,
                                                            'tx_confirmation': tx['confirmation'],
                                                            'tx_lock_icon': tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i> ' : '',
                                                            'tx_lock_cls': tx['confirmation'] < 10 ? "tx-lock" : "",
                                                            'tx_note': tx['note'],
                                                            'tx_note_hide': tx['note'].length > 0 ? "" : "tx-note-hide",
                                                            'tx_destinations' : dest_html,
                                                            'tx_destinations_hide': tx.hasOwnProperty('destinations') ? "" : "tx-destinations-hide"
                                                       });
                    
                    hide_progress();
                    show_app_dialog('<div class="copied">' + tx_rendered + '</div>');
                });
                
                app_hub.on_load_tx_history_completed_event.connect(function(ret_json){
                    var ret = $.parseJSON(ret_json);
                    var txs = ret["txs"];
                    var current_page = ret["current_page"];
                    var num_of_pages = ret["num_of_pages"];
                    var start_page = ret["start_page"];
                    var end_page = ret["end_page"];
                    
                    var tx_history_row_tmpl = $('#tx_history_row').html();
                    var table_tx_history_body = $('#table_tx_history tbody');
                    table_tx_history_body.html("");
                    for(var i=0; i<txs.length; i++){
                        var tx = txs[i];
                        var row = Mustache.render(tx_history_row_tmpl, {
                            'tx_status': tx['confirmation'] == 0 ? '<i class="fa fa-clock-o"></i>' : ( tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i>' : '<i class="fa fa-unlock"></i>' ),
                            'tx_direction': tx['direction'] == "in" ? '<i class="fa fa-mail-forward"></i>' : '<i class="fa fa-reply"></i>',
                            'tx_date_time': dateConverter(tx['timestamp']) + ' ' + timeConverter(tx['timestamp']),
                            'tx_id': tx['txid'],
                            'tx_id_short': tx['txid'].substring(0, 26) + "...",
                            'tx_payment_id': tx['payment_id'].substring(0, 16),
                            'tx_amount': printMoney(tx['amount']/1000000000.),
                            'tx_height': tx['height'],
                            'cls_in_out': tx['status']
                        });
                        
                        table_tx_history_body.append(row);
                    }
                    
                    if(num_of_pages > 1){
                        var page_html = "";
                        for(var i=start_page; i<=end_page; i++){
                            page_html += '<li class="' + (i == current_page ? 'active' : '') + '"><a href="javascript:load_tx_history(' + i + ')">' + i + '</a></li>';
                        }
                        
                        var tx_history_page_tmpl = $('#tx_history_page_tmpl').html();
                        var tx_history_page_html =  Mustache.render(tx_history_page_tmpl, {
                            'page_prev_disabled': current_page == 1? 'disabled': '',
                            'page_next_disabled': current_page == num_of_pages ? 'disabled' : '',
                            'prev_page': current_page > 1 ? current_page - 1 : current_page,
                            'next_page': current_page < num_of_pages ? current_page + 1 : current_page,
                            'page_html': page_html
                        });
                        
                        $('#tx_history_pages').html('');
                        $('#tx_history_pages').append(tx_history_page_html);
                    }
                    
                    current_tx_history_page = current_page;
                });
                
                app_hub.on_view_wallet_key_completed_event.connect(function(title, ret){
                    if(ret){
                        var html = '<h5>' + title + '</h5>';
                        html += '<div class="form-group">';
                        html +='<textarea class="form-control address-box copied" style="height:70px;font-size:95%;" readonly="readonly">' + ret + '</textarea>';
                        html += '</div>';
                        show_app_dialog(html);
                    }
                });
                
                app_hub.on_restart_daemon_completed_event.connect(function(){
                    hide_progress();
                });
            }
            
            function delete_address(index){
                hide_app_dialog();
                show_progress("Deleting address book entry...");
                app_hub.delete_address_book(index);
                return false;
            }
            
            function update_daemon_status(status_json){
                setTimeout(function(){
                    var status = $.parseJSON(status_json);
                    var daemon_status = status['status'];
                    var current_height = status['current_height'];
                    var target_height = status['target_height'];
                    sync_pct = target_height > 0 ? parseInt(current_height*100/target_height) : 0;
                    var status_text = "Network: " + daemon_status;
                    if(daemon_status == "Connected"){
                        if(sync_pct == 100){
                            status_text = '<i class="fa fa-rss fa-flip-horizontal"></i>&nbsp;&nbsp;Network synchronized';
                        }
                        else {
                            status_text = '<i class="fa fa-refresh"></i>&nbsp;&nbsp;Synchronizing...';
                        }
                    }
                    status_text += " " + current_height + "/" + target_height + " (<strong>" + sync_pct + "%</strong>)";
                    progress_bar_text_low.html(status_text);
                    progress_bar_text_high.html(status_text);
                                                    
                    if(sync_pct < 100){
                        progress_bar.addClass('progress-bar-striped')
                                                        .addClass('active');
                    }
                    else{
                        progress_bar.removeClass('progress-bar-striped')
                                                        .removeClass('active');
                    }
                    
                    progress_bar.removeClass('progress-bar-success')
                                    .removeClass('progress-bar-warning')
                                    .removeClass('progress-bar-danger');
                    if(sync_pct >= 95) progress_bar.addClass('progress-bar-success');
                    else if(sync_pct >= 30) progress_bar.addClass('progress-bar-warning');
                    else progress_bar.addClass('progress-bar-danger');
                    
                    if(sync_pct < 36){
                        progress_bar_text_low.show();
                        progress_bar_text_high.hide();
                    }
                    else{
                        progress_bar_text_low.hide();
                        progress_bar_text_high.show();
                    }
                    
                    progress_bar.css("width", sync_pct + "%");
                    progress_bar.attr("aria-valuenow", sync_pct);
                    
                    disable_buttons(sync_pct < 100);
                }, 1);
                
            }
            
            
            function update_wallet_info(wallet_info_json){
                setTimeout(function(){
                    var wallet_info = $.parseJSON(wallet_info_json);
                    var recent_txs = wallet_info['recent_txs'];
                    var recent_tx_row_tmpl = $('#recent_tx_row_templ').html();
                    
                    if(recent_txs.length > 0){
                        recent_txs_div.html('');
                        for(var i=0; i < recent_txs.length; i++){
                            var tx = recent_txs[i];
                            var tx_status_text = tx['status'] == "in" || tx['status'] == "out" ? "Completed" :  (tx['status'] == "pending" ? "Pending" : "In Pool");
                            if(tx['confirmation'] < 10){
                                if(tx_status_text == "Completed") tx_status_text = "Locked";
                                tx_status_text += " (+" + tx['confirmation'] + " confirms)";                
                            }
                            
                            var tx_rendered = Mustache.render(recent_tx_row_tmpl, 
                                                        {   'cls_in_out': tx['status'],
                                                            'tx_direction': tx['direction'],
                                                            'tx_status': tx_status_text,
                                                            'tx_fa_icon': tx['direction'] == "in" ? "mail-forward" : "reply",
                                                            'tx_id': tx['txid'],
                                                            'tx_payment_id': tx['payment_id'], 
                                                            'tx_amount': printMoney(tx['amount']/1000000000.),
                                                            'tx_fee': printMoney(tx['fee']/1000000000.),
                                                            'tx_fee_hide': tx['fee'] > 0 ? '' : 'tx-fee-hide',
                                                            'tx_date': dateConverter(tx['timestamp']),
                                                            'tx_time': timeConverter(tx['timestamp']),
                                                            'tx_height': tx['height'] > 0 ? tx['height'] : "?",
                                                            'tx_confirmation': tx['confirmation'],
                                                            'tx_lock_icon': tx['confirmation'] < 10 ? '<i class="fa fa-lock"></i> ' : '',
                                                            'tx_lock_cls': tx['confirmation'] < 10 ? "tx-lock" : ""
                                                        });
                            recent_txs_div.append(tx_rendered);
                        }
                    }
                    
                    disable_buttons(sync_pct < 100);
                                        
                    if(current_balance != wallet_info['balance']){
                        balance_span.delay(100).fadeOut(function(){
                            balance_span.html( printMoney(wallet_info['balance']) );
                        }).fadeIn('slow');
                        current_balance = wallet_info['balance'];
                    }
                    
                    if(current_unlocked_balance != wallet_info['unlocked_balance']){
                        unlocked_balance_span.delay(100).fadeOut(function(){
                            unlocked_balance_span.html( printMoney(wallet_info['unlocked_balance']) );
                        }).fadeIn('slow');
                        current_unlocked_balance = wallet_info['unlocked_balance'];
                    }
            
                    if(current_address != wallet_info['address']){
                        current_address = wallet_info['address'];
                        receive_address.val(current_address);
                    }
                    
                    var table_body = $('#table_new_subaddresses tbody');
                    var new_subaddress_row_tmpl = $('#new_subaddress_row_tmpl').html();
                    var new_subaddresses = wallet_info['new_subaddresses'];
                    
                    table_body.html('');
                    
                    for(var i=0; i < new_subaddresses.length; i++){
                        var subaddress = new_subaddresses[i];
                        var row_rendered = Mustache.render(new_subaddress_row_tmpl, 
                            {   'address_index': subaddress['address_index'],
                                'address' : subaddress['address'],
                                'address_short' : subaddress['address'].substr(0, 70) + '...'
                            });
                        
                            
                        table_body.append(row_rendered);
                    }
                    
                    table_body = $('#table_used_subaddresses tbody');
                    var used_subaddress_row_tmpl = $('#used_subaddress_row_tmpl').html();
                    var used_subaddresses = wallet_info['used_subaddresses'];
                    
                    table_body.html('');
                    
                    for(var i=0; i < used_subaddresses.length; i++){
                        var subaddress = used_subaddresses[i];
                        var row_rendered = Mustache.render(used_subaddress_row_tmpl, 
                            {   'address_index': subaddress['address_index'],
                                'address' : subaddress['address'],
                                'address_short' : subaddress['address'].substr(0, 40) + '...',
                                'balance': subaddress['balance'],
                                'unlocked_balance': subaddress['unlocked_balance'],
                                'row_font_weight': subaddress['address_index'] == 0 ? 'bold' : 'normal'
                            });
                        
                            
                        table_body.append(row_rendered);
                    }
                    
                    hide_app_progress();
                    $('[data-toggle="tooltip"]').tooltip();
                    
                }, 1);
            }
            
            function show_qrcode(text){
                $('#qrcode_dialog_body').html('');
                $('#qrcode_dialog_body').qrcode({width: 200,height: 200, text: text});
                $('#qrcode_dialog').modal('show');
                
            }
            
            function disable_buttons(s){
                rescan_spent_btn.disable(s);
                rescan_bc_btn.disable(s);
                btn_send_tx.disable(s);
                btn_fill_all_money.disable(s);
                
                syncing.each(function(index, value){
                    s ? $(this).show() : $(this).hide();
                });
                
                balance_span.css("color", s ? "#ccc" : "#666");
                unlocked_balance_span.css("color", s ? "#ccc" : "#666");
            }
            
            function rescan_spent(){
                rescan_spent_btn.disable(true);
                rescan_bc_btn.disable(true);
                show_progress("Rescan spent...");
                app_hub.rescan_spent();
                return false;
            }
            
            function rescan_bc(){
                rescan_spent_btn.disable(true);
                rescan_bc_btn.disable(true);
                show_progress("Rescan blockchain...");
                app_hub.rescan_bc();
                return false;
            }
            
            function fill_all_money(){
                $('#send_amount').val(current_unlocked_balance);
                return false;
            }
            
            function send_tx(){
                var amount = $('#send_amount').val().trim();
                var sweep_all = false;
                var errors = [];
                amount = parseFloat(amount);
                
                if(!amount || amount < 0)
                {
                    errors.push("Send amount must be a positive number!");
                    $('#send_amount').parent().addClass('has-error');
                }
                else if(amount > current_unlocked_balance){
                    errors.push("Send amount is more than unlocked balance!");
                    $('#send_amount').parent().addClass('has-error');
                }
                else{
                    if(amount == current_unlocked_balance){
                        sweep_all = true;
                    }
                    $('#send_amount').parent().removeClass('has-error');
                }
                
                var address = $('#send_address').val();
                if(!address){
                    errors.push("Address is required!");
                    $('#send_address').parent().addClass('has-error');
                }
                else if(!((address.substr(0, 4) == "Sumo" && address.length == 99) || 
                    (address.substr(0, 4) == "Sumi"  && address.length == 110) || 
                    (address.substr(0, 4) == "Subo"  && address.length == 98)))
                {
                    errors.push("Address is not valid!");
                    $('#send_address').parent().addClass('has-error');
                }
                else{
                    $('#send_address').parent().removeClass('has-error');
                }
                
                var payment_id = $('#send_payment_id').val().trim();
                if(payment_id && !(payment_id.length == 16 || payment_id.length == 64)){
                    errors.push("Payment ID must be a 16 or 64 hexadecimal-characters string!");
                    $('#send_payment_id').parent().addClass('has-error');
                }
                else{
                    $('#send_payment_id').parent().removeClass('has-error');
                }
                
                if(errors.length > 0){
                    var msg = "<ul>";
                    for(var i=0; i<errors.length;i++){
                        msg += "<li>" + errors[i] + "</li>";
                    }
                    msg += "</ul>";
                    show_alert(msg);
                    return false;
                }
                
                var tx_desc = $('#send_tx_desc').val().trim();
                var priority = $('#send_priority').val();
                var mixin = $('#send_mixins').val();
                
                btn_send_tx.disable(true);
                show_progress("Sending coins... This can take a while for big amount...");
                app_hub.send_tx(amount, address, payment_id, priority, mixin, tx_desc, $('#checkbox_save_address').is(":checked"), sweep_all);
                return false;
            }
            
            function generate_payment_id(){
                show_progress("Generating payment ID, integrated address...");
                app_hub.generate_payment_id(16);
                return false;
            }
            
            function copy_address(){
                $('#btn_copy_address').tooltip('show');
                //receive_address.select();
                app_hub.copy_text(receive_address.val());
                setTimeout(function(){
                    $('#btn_copy_address').tooltip('hide');
                }, 1000);
                return false;
            }
            
            function qr_address(){
                show_qrcode(receive_address.val());
                return false;
            }
            
            function copy_subaddress(el, subaddress_text){
                $(el).tooltip('show');
                app_hub.copy_text(subaddress_text);
                setTimeout(function(){
                    $(el).tooltip('hide');
                }, 1000);
                return false;
            }
            
            
            function copy_integrated_address(){
                $('#btn_copy_integrated_address').tooltip('show');
                receive_integrated_address.select();
                app_hub.copy_text(receive_integrated_address.val());
                setTimeout(function(){
                    $('#btn_copy_integrated_address').tooltip('hide');
                }, 1000);
                return false; 
            }
            
            function view_tx_detail(height, tx_id){
                show_progress("Load tx details...");
                app_hub.view_tx_detail(height == "?" ? 0 : parseInt(height), tx_id);
                return false;
            }
            
            function load_tx_history(page){
                app_hub.load_tx_history(page);
                return false;
            }
            
            
            function show_address_book(){
                show_progress("Loading address book...");
                app_hub.load_address_book();
                return false;
            }
            
            function open_new_wallet(){
                app_hub.open_new_wallet();
                return false;
            }
            
            function view_wallet_key(key_type){
                app_hub.view_wallet_key(key_type);
                return false;
            }
            
            function set_daemon_log_level(level){
                console.log(level);
                app_hub.set_daemon_log_level(level);
            }
            
            function set_block_sync_size(sync_size){
                app_hub.set_block_sync_size(sync_size);
            }
            
            function about_app(){
                app_hub.about_app();
                return false;
            }
            
            function show_app_dialog(msg, title){
                $('#app_model_body').css("color", "#666"); 
                $('#app_model_body').html(msg);
                $('#btn_copy').text('Copy');
                $('#app_modal_dialog').modal('show');
            }
            
            function hide_app_dialog(){
                $('#app_modal_dialog').modal('hide');
            }
            
            function show_alert(msg, title){
                $('#app_model_body').css("color", "#c7254e"); 
                $('#app_model_body').html(msg);
                $('#app_modal_dialog').modal('show');
            }
            
            function show_app_progress(msg){
                $('#app_modal_progress_text').html(msg);
                $('#app_modal_progress').modal('show');
            }
            
            function hide_app_progress(){
                $('#app_modal_progress').modal('hide');
            }
            
            function show_progress(msg){
                $('#sending_modal_progress_text').html(msg);
                $('#sending_modal_progress').modal('show');
            }
            
            function hide_progress(){
                $('#sending_modal_progress').modal('hide');
            }
            
            function open_link(link){
                app_hub.open_link(link);
                return false;
            }
            
            function restart_daemon(){
                show_app_progress("Restarting daemon...");
                app_hub.restart_daemon();
                return false;
            }
            
            function copy_dialog_content(){
                app_hub.copy_text( $('#app_model_body .copied').text() );
                $('#btn_copy').text('Copied');
            }
 
            $(document).ready(function(){
                progress_bar_text_low = $('#progress_bar_text_low');
                progress_bar_text_high = $('#progress_bar_text_high');
                progress_bar = $('#progress_bar');
                balance_span = $('#balance');
                unlocked_balance_span = $('#unlocked_balance');
                rescan_spent_btn = $('#btn_rescan_spent');
                rescan_bc_btn = $('#btn_rescan_bc');
                syncing = $('.syncing');
                wallet_address = $('#wallet_address');
                btn_send_tx = $('#btn_send_tx');
                btn_fill_all_money = $('#btn_fill_all_money');
                recent_txs_div = $('#recent_txs');
               
                current_balance = null;
                current_unlocked_balance = null;
                current_address = null;
                
                current_tx_history_page = 1;
                
                sync_pct = 0;
                show_app_progress("Loading wallet...");
                
                receive_address = $('#receive_address');
                receive_integrated_address = $("#receive_integrated_address");
                
                receive_address.focus(function() {
                    var $this = $(this);
                    $this.select();
                    $this.mouseup(function() {
                        $this.unbind("mouseup");
                        return false;
                    });
                });
                
                receive_integrated_address.focus(function() {
                    var $this = $(this);
                    $this.select();
                    $this.mouseup(function() {
                        $this.unbind("mouseup");
                        return false;
                    });
                });
                
                $('[data-toggle="tooltip"]').tooltip();
                 
                $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
                    var target = $(this).attr('href');
                                        
                    if(current_tx_history_page == 1 && target == "#tx_history_tab"){
                        setTimeout(function(){
                            load_tx_history(current_tx_history_page);
                        }, 1);
                    }
                });
            });
        </script>
    </head>
    <body>
        <div class="container">
            <ul class="nav nav-tabs">
              <li><a data-toggle="tab" href="#receive_tab"><i class="fa fa-arrow-circle-o-down"></i> Receive</a></li>
              <li class="active"><a data-toggle="tab" href="#balance_tab"><i class="fa fa-money"></i> Wallet</a></li>
              <li><a data-toggle="tab" href="#send_tab"><i class="fa fa-send-o"></i> Send</a></li>
              <li><a data-toggle="tab" href="#tx_history_tab"><i class="fa fa-history"></i> TX History</a></li>
              <li><a data-toggle="tab" href="#settings_tab"><i class="fa fa-cogs"></i> Settings</a></li>
            </ul>
            <div class="tab-content" style="height:490px; margin-top:20px;">
                <div id="receive_tab" class="tab-pane fade">
                    <h3>RECEIVE</h3>
                    <form id="form_receive" class="form-horizontal">
                        <div class="form-group">
                            <div class="col-sm-12">
                                <label for="receive_address" class="col-xs-2 control-label">Main Address</label>
                                <div class="col-xs-10 input-group" style="padding-left: 15px; padding-right: 15px;">
                                    <input id="receive_address" type="text" class="form-control" style="font-weight: bold" maxlength="64" readonly />
                                    <span class="input-group-btn">
                                        <button id="btn_copy_address" class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="copy_address()" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                                        <button id="btn_qr_address" class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="qr_address()" title="Show QR code"><i class="fa fa-qrcode"></i></button>
                                    </span>
                                </div>
                            </div>
                        </div>
                    </form>
                    <div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true" style="margin-left: 15px; margin-right: 15px;">
                        <div class="panel panel-default">
                          <div class="panel-heading" role="tab" id="headingOne">
                            <h4 class="panel-title">
                            <a role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
                              Used Addresses
                            </a>
                          </h4>
                          </div>
                          <div id="collapseOne" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingOne">
                            <div class="panel-body">
                                <div class="table-responsive">
                                    <table id="table_used_subaddresses" class="table table-hover table-striped table-condensed">
                                        <thead>
                                            <tr>
                                                <th>Address</th>
                                                <th style="text-align: right">Balance</th>
                                                <th style="text-align: right">Unlocked</th>
                                                <th style="text-align: right">Index</th>
                                                <th>&nbsp;</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                          </div>
                        </div>
                        <div class="panel panel-default">
                          <div class="panel-heading" role="tab" id="headingTwo">
                            <h4 class="panel-title">
                            <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">
                              New (Ghost) Addresses
                            </a>
                          </h4>
                          </div>
                          <div id="collapseTwo" class="panel-collapse collapse in" role="tabpanel" aria-labelledby="headingTwo">
                            <div class="panel-body" style="overflow: auto">
                                <div class="table-responsive">
                                    <table id="table_new_subaddresses" class="table table-hover table-striped table-condensed">
                                        <thead>
                                            <tr>
                                                <th>Address</th>
                                                <th style="text-align: right">Index</th>
                                                <th>&nbsp;</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                          </div>
                        </div>
                    </div>
                </div>
                <div id="balance_tab" class="tab-pane fade in active">
                    <h3>BALANCE</h3>
                    <div class="row">
                        <div class="col-sm-12">
                            <div class="col-xs-6">
                                <h5><i class="fa fa-fw fa-balance-scale"></i> Balance:</h5>
                                <h5><i class="fa fa-fw fa-unlock"></i> Unlocked Balance:</h5>
                            </div>
                            <div class="col-xs-6" style="text-align:right">
                                <h5><span id="balance">0.000000000</span> <small>SUMO</small> <span class="syncing"> (syncing)</span></h5>
                                <h5><span id="unlocked_balance">0.000000000</span> <small>SUMO</small> <span class="syncing"> (syncing)</span></h5>
                            </div>
                            <div class="col-xs-12" style="margin-top: 10px">
                                <button id="btn_rescan_spent" type="button" class="btn btn-primary" onclick="rescan_spent()" disabled><i class="fa fa-sort-amount-desc"></i> Rescan Spent</button>
                                <button id="btn_rescan_bc" type="button" class="btn btn-primary" style="margin-left: 20px;" onclick="rescan_bc()" disabled><i class="fa fa-repeat"></i> Rescan Blockchain</button>
                            </div>
                        </div>
                    </div>
                    <hr style="margin-top:20px;margin-bottom:10px;">
                    <h3>RECENT TRANSACTIONS</h3>
                    <div class="row" id="recent_txs">
                       <h4 style="color:#ddd;text-align:center;margin-top:70px;">NO TRANSACTIONS FOUND</h4>
                    </div>
                </div>
                <div id="send_tab" class="tab-pane fade">
                    <h3>SEND</h3>
                    <form id="form_send_tx" class="form-horizontal">
                        <fieldset>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_amount" class="col-xs-2 control-label">Amount</label>
                                    <div class="col-xs-10 input-group" style="padding-left: 15px;padding-right: 15px;">
                                        <input id="send_amount" type="text" class="form-control" placeholder="0.0" maxlength="255"/>
                                        <span class="input-group-btn">
                                            <button id="btn_fill_all_money" class="btn btn-primary btn-sm"  style="text-transform: none" type="button" tabindex="-1" onclick="fill_all_money()" disabled>All coins</button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_address" class="col-xs-2 control-label">Address</label>
                                    <div class="col-xs-10 input-group" style="padding-left: 15px; padding-right: 15px;">
                                        <input id="send_address" type="text" class="form-control"  placeholder="Paste receiving address here (Ctrl+V)..." maxlength="110"/>
                                        <span class="input-group-btn">
                                            <button class="btn btn-primary btn-sm" style="text-transform: none" type="button" tabindex="-1" onclick="show_address_book()">
                                                <i class="fa fa-address-book"></i> Address book...
                                            </button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_payment_id" class="col-xs-2 control-label">Payment ID</label>
                                    <div class="col-xs-10">
                                        <input id="send_payment_id" type="text" class="form-control"  placeholder="Paste payment ID here (Ctrl+V, optional)..." maxlength="64"/>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12">
                                    <label for="send_tx_desc" class="col-xs-2 control-label">Description</label>
                                    <div class="col-xs-10">
                                        <input id="send_tx_desc" type="text" class="form-control"  placeholder="Tx description, saved to local wallet history (optional)..." maxlength="255"/>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-6">
                                    <label for="send_mixins" class="col-xs-4 control-label">Privacy <sup>1</sup></label>
                                    <div class="col-xs-8">
                                        <select id="send_mixins" class="form-control">
                                          <option value="12" selected>12 mixins (default)</option>
                                          <option value="15">15 mixins</option>
                                          <option value="18">18 mixins</option>
                                          <option value="24">24 mixins</option>
                                          <option value="36">36 mixins</option>
                                          <option value="48">48 mixins</option>
                                          <option value="60">60 mixins</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <label for="send_priority" class="col-xs-4 control-label">Priority <sup>2</sup></label>
                                    <div class="col-xs-8">
                                        <select id="send_priority" class="form-control">
                                          <option value="1" selected>Normal (x1 fee)</option>
                                          <option value="2">High (x2 fee)</option>
                                          <option value="4">Higher (x4 fee)</option>
                                          <option value="20">Elevated (x20 fee)</option>
                                          <option value="166">Forceful (x166 fee)</option>
                                        </select>
                                       <!--<input id="send_fee_level_slider" type="text"/>--> 
                                    </div>
                                </div>
                            </div>
                             <div class="form-group">
                                <div class="col-sm-12">
                                    <label class="col-xs-2 control-label sr-only">&nbsp;</label>
                                    <div class="col-xs-10">
                                        <input id="checkbox_save_address" type="checkbox" /> <label for="checkbox_save_address">Save address (with payment id) to address book</label>
                                        <label style="color:#999"><small>1. Higher mixin (ringsize) means higher transaction cost, using default mixin# (12) is recommended</small></label>
                                        <label style="color:#999"><small>2. Only choose higher priority when there are many transactions in tx pool or "Normal" works just fine</small></label>
                                    </div>
                                </div>
                            </div>
                            <div class="form-group">
                                <div class="col-sm-12" style="text-align: center">
                                    <button id="btn_send_tx" type="button" class="btn btn-success" onclick="send_tx()" disabled><i class="fa fa-send"></i> Send</button>
                                </div>
                            </div>
                        </fieldset>
                    </form>
                </div>
                <div id="tx_history_tab" class="tab-pane fade">
                    <div class="table-responsive">
                        <table id="table_tx_history" class="table table-hover table-striped table-condensed">
                            <thead>
                                <tr>
                                    <th>?</th>
                                    <th>I/O</th>
                                    <th>Date/Time</th>
                                    <th>Tx ID</th>
                                    <th>Payment ID</th>
                                    <th style="text-align: right">Amount</th>
                                    <th>&nbsp;</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="7" style="text-align: center">
                                        <nav aria-label="Page navigation">
                                            <ul id="tx_history_pages" class="pagination pagination-sm" style="margin: 5px 0;">
                                            </ul>
                                        </nav>
                                    <td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
                <div id="settings_tab" class="tab-pane fade">
                    <h3>WALLET</h3>
                    <div class="row">
                        <div class="col-sm-12 wallet-settings">
                            <button id="btn_new_wallet" type="button" class="btn btn-primary" onclick="open_new_wallet()"><i class="fa fa-file"></i> New Wallet...</button>
                            <button id="btn_view_seed" type="button" class="btn btn-primary" onclick="view_wallet_key('mnemonic')"><i class="fa fa-eye"></i> Mnemonic Seed...</button>
                            <button id="btn_view_viewkey" type="button" class="btn btn-primary" onclick="view_wallet_key('view_key')"><i class="fa fa-key"></i> Viewkey...</button>
                            <button id="btn_view_spendkey" type="button" class="btn btn-primary" onclick="view_wallet_key('spend_key')"><i class="fa fa-key"></i> Spendkey...</button>
                        </div>
                    </div>
                    <hr style="margin-top:20px;margin-bottom:10px;">
                    <h3>DAEMON</h3>
                    <div class="row">
                        <div class="col-lg-12">
                            <div class="col-sm-5">
                                <form class="form-horizontal">
                                    <div class="form-group">
                                        <label class="col-xs-4 control-label">Log level:</label>
                                        <div class="col-xs-8">
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_0" value="0" onclick="set_daemon_log_level(0)" checked="">
                                                Level 0 (default)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_1" value="1" onclick="set_daemon_log_level(1)">
                                                Level 1
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_2" value="2" onclick="set_daemon_log_level(2)">
                                                Level 2
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_3" value="3" onclick="set_daemon_log_level(3)">
                                                Level 3
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_log_level" id="daemon_log_level_4" value="4" onclick="set_daemon_log_level(4)">
                                                Level 4
                                              </label>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="col-sm-7">
                                <form class="form-horizontal">
                                    <div class="form-group">
                                        <label class="col-xs-4 control-label">Block sync size:</label>
                                        <div class="col-xs-8">
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_10" value="10" onclick="set_block_sync_size(10)" checked="">
                                                10 (default, for slow network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_20" value="20" onclick="set_block_sync_size(20)">
                                                20 (for normal network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_50" value="50" onclick="set_block_sync_size(50)">
                                                50 (for good network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_100" value="100" onclick="set_block_sync_size(100)">
                                                100 (for better network)
                                              </label>
                                            </div>
                                            <div class="radio">
                                              <label>
                                                <input type="radio" name="daemon_block_sync_size" id="block_sync_size_200" value="200" onclick="set_block_sync_size(200)">
                                                200 (for great network)
                                              </label>
                                            </div>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            <div class="col-sm-12 wallet-settings" style="margin-top: 10px; text-align:center;">
                                <button id="btn_restart_daemon" type="button" class="btn btn-primary" onclick="restart_daemon()"><i class="fa fa-refresh"></i> Restart Daemon</button>
                                <button id="btn_view_log" type="button" class="btn btn-primary" onclick="app_hub.view_daemon_log()"><i class="fa fa-file"></i> View Log...</button>
                            </div>
                        </div>
                    </div>
                    <hr style="margin-top:10px;margin-bottom:10px;">
                    <div class="row">
                        <div class="col-sm-12" style="margin-top: 10px;text-align: center">
                            <button id="btn_about" type="button" class="btn btn-primary" onclick="about_app()"><i class="fa fa-user"></i> About...</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="progress" role="application">
                <div id="progress_bar" class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width:1%;">
                    <span id="progress_bar_text_high"></span>
                </div>
                <span id="progress_bar_text_low"><i class="fa fa-flash"></i>&nbsp;&nbsp;Connecting to network...</span>
            </div>
        </div>
        
        <div class="modal" id="app_modal_dialog" style="z-index: 100000;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body" id="app_model_body"></div>
                    <div class="modal-footer">
                        <button id="btn_copy" type="button" class="btn btn-primary" onclick="copy_dialog_content()">Copy</button>
                        <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal" id="sending_modal_progress" style="z-index: 100001;" data-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <p><i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i><span id="sending_modal_progress_text" class="modal-progress-text"></span></p>
                    </div>
                </div>
            </div>
        </div>
        <div class="modal" id="app_modal_progress" style="z-index: 100002;" data-backdrop="static">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-body">
                        <p><span id="app_modal_progress_text" class="modal-progress-text"></span><p>
                        <!--<p style="text-align: center"><img src="./images/ajax-loader2.gif"/></p>-->
                        <p style="text-align: center"><i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i></p> 
                    </div>
                </div>
            </div>
        </div>
        
        <div class="modal" id="qrcode_dialog" style="z-index: 100003;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" style="text-align:center" id="qrcode_dialog_body"></div>
                    <div class="modal-footer">
                        
                    </div>
                </div>
            </div>
        </div>
        
        <script id="recent_tx_row_templ" type="x-tmpl-mustache">
            <div class="col-sm-12">
                <div class="col-xs-10" style="padding-right:0">
                    <p class="tx-list tx-{{cls_in_out}}"><i class="fa fa-{{ tx_fa_icon }}"></i> ({{tx_direction}}) <span class="tx-list txid"><a href="javascript:open_link('https://explorer.sumokoin.com/tx/{{ tx_id }}')" title="View on blockchain explorer">{{ tx_id }}</a></span></p>
                    Payment ID: <span class="tx-list tx-payment-id">{{ tx_payment_id }}</span><br/>
                    Height: <span class="tx-list tx-height">{{ tx_height }}</span>  Date: <span class="tx-list tx-date">{{ tx_date }}</span> Time: <span class="tx-list tx-time">{{ tx_time }}</span> Status: <span class="tx-list tx-status">{{ tx_status }}</span><br/>
                    <p style="font-size:140%">Amount: <span class="tx-list tx-{{cls_in_out}} tx-amount {{tx_lock_cls}}">{{{tx_lock_icon}}}{{ tx_amount }}</span> <span class="{{ tx_fee_hide }}">Fee:</span> <span class="tx-list tx-{{cls_in_out}} tx-fee {{ tx_fee_hide }}">{{ tx_fee }}</span></p> 
                </div>
                <div class="col-xs-2">
                    <button class="btn btn-warning" onclick="view_tx_detail('{{ tx_height }}', '{{ tx_id }}')">Details</button>
                </div>
                <br clear="both"/><hr style="margin: 0 0 10px"/>
            </div>
        </script>
        
        <script id="tx_detail_templ" type="x-tmpl-mustache">
            <p class="tx-list tx-{{cls_in_out}}" style="font-size: 90%"><i class="fa fa-{{ tx_fa_icon }}"></i> {{tx_direction}}<br>
                <span class="tx-list txid"><a href="javascript:open_link('https://explorer.sumokoin.com/tx/{{ tx_id }}')" title="View on blockchain explorer">{{ tx_id }}</a></span>
            </p>
            <ul style="font-size: 90%">
                <li>Payment ID: <span class="tx-list tx-payment-id">{{ tx_payment_id }}</span></li>
                <li>Height: <span class="tx-list tx-height">{{ tx_height }}</span>  Date: <span class="tx-list tx-date">{{ tx_date }}</span> Time: <span class="tx-list tx-time">{{ tx_time }}</span></li>
                <li>Status: <span class="tx-list tx-status">{{ tx_status }}</span></li>
                <li>Amount: <span class="tx-list tx-{{cls_in_out}} tx-amount {{tx_lock_cls}}">{{{tx_lock_icon}}}{{ tx_amount }}</span> <span class="{{ tx_fee_hide }}">Fee:</span> <span class="tx-list tx-{{cls_in_out}} tx-fee {{ tx_fee_hide }}">{{ tx_fee }}</span></li>
                <li class="{{ tx_note_hide }}">Tx Note: <span class="tx-list tx-note">{{ tx_note }}</span></li>
            </ul>
            <div class="tx-destinations {{ tx_destinations_hide }}">
                <span style="margin-left:10px;">Destination(s):</span>
                <ul>
                    {{{ tx_destinations }}}
                </ul>
            </div>
        </script>
        
        <script id="address_book_row_templ" type="x-tmpl-mustache">
            <tr>
                <td width="160px" class="address-book-row" data-address="{{ address }}" data-payment-id="{{ payment_id }}"><a href="#" title="{{ address }}">{{ address_short }}</a></td>
                <td width="150px" class="address-book-row" data-address="{{ address }}" data-payment-id="{{ payment_id }}">{{ payment_id_short }}</a></td>
                <td width="200px" class="address-book-row" data-address="{{ address }}" data-payment-id="{{ payment_id }}">{{ desc_short }}</a></td>
                <td width="50px"><button type="button" class="btn btn-default btn-xs" onclick="delete_address({{ index }})"><i class="fa fa-remove"></i> Delete</button></td>
            </tr>
        </script>
        
        <script id="tx_history_row" type="x-tmpl-mustache">
            <tr class="tx-list tx-{{ cls_in_out }}" style="font-weight: normal;">
                <td align="center">{{{ tx_status }}}</td>
                <td align="center">{{{ tx_direction }}}</td>
                <td>{{ tx_date_time }}</td>
                <td>{{ tx_id_short }}</td>
                <td>{{ tx_payment_id }}</td>
                <td align="right">{{ tx_amount }}</td>
                <td><button class="btn btn-default btn-sm" onclick="view_tx_detail('{{ tx_height }}', '{{ tx_id }}')">Details</button></td>
            </tr>
        </script>
        
        <script id="tx_history_page_tmpl" type="x-tmpl-mustache">
            <li class="{{ page_prev_disabled }}">
                <a href="javascript:load_tx_history({{ prev_page }})" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
            {{{ page_html }}}
            <li class="{{ page_next_disabled }}">
                <a href="javascript:load_tx_history({{ next_page }})" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        </script>
        
        <script id="new_subaddress_row_tmpl" type="x-tmpl-mustache">
            <tr class="" style="font-weight: normal;color:#333;">
                <td>{{ address_short }}</td>
                <td align="right">{{ address_index }}</td>
                <td align="right">
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="copy_subaddress(this, '{{ address }}')" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="show_qrcode('{{ address }}')" title="Show QR code"><i class="fa fa-qrcode"></i></button>    
                </td>
            </tr>
        </script>
        
        <script id="used_subaddress_row_tmpl" type="x-tmpl-mustache">
            <tr class="" style="font-weight:{{ row_font_weight }};color:#333;">
                <td>{{ address_short }}</td>
                <td align="right">{{ balance }}</td>
                <td align="right">{{ unlocked_balance }}</td>
                <td align="right">{{ address_index }}</td>
                <td align="right">
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="copy_subaddress(this, '{{ address }}')" data-toggle="tooltip" data-placement="bottom" data-trigger="manual" title="Address copied"><i class="fa fa-copy"></i></button>
                    <button class="btn btn-primary btn-sm" tabindex="-1" onclick="show_qrcode('{{ address }}')" title="Show QR code"><i class="fa fa-qrcode"></i></button>    
                </td>
            </tr>
        </script>
    </body>
</html>
"""