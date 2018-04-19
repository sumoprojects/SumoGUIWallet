#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2017, The Sumokoin Project (www.sumokoin.org)
'''
New wallet HTML
'''

html ="""
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <script src="./scripts/jquery-1.9.1.min.js"></script>
        <script src="./scripts/utils.js"></script>
        <script type="text/javascript">
            function app_ready(){
                app_hub.on_new_wallet_show_progress_event.connect(show_progress);
                app_hub.on_new_wallet_show_info_event.connect(show_wallet_info);
                app_hub.on_new_wallet_ui_reset_event.connect(reset_ui);
                app_hub.on_new_wallet_update_processed_block_height_event.connect(update_processed_block_height);
                app_hub.on_paste_seed_words_event.connect(function(text){
                    $('#seed').val(text);
                });
            }
            
            function create_new_wallet(){
                app_hub.create_new_wallet('', 0);
                return false;
            }
            
            function restore_wallet(){
                var seed = $('#seed').val();
                var restore_height = $('#restore_height_txt').val();
                seed = replaceAll(seed, "\\n", " ");
                if(seed.length == 0 || seed.split(" ").length != 26)
                    alert("Please paste 26 mnemonic seed words to above box", "Seed words required!");
                else{
                    var h =  !isNaN(parseInt(restore_height)) ? parseInt(restore_height) : 0;
                    if(h < 0) h = 0;
                    app_hub.create_new_wallet(seed, h);
                }
                return false;
            }
            
            function import_wallet(){
                app_hub.import_wallet();
                return false;
            }
            
            function show_progress(header){
                $('#gen_wallet_btn').disable(true);
                $('#restore_wallet_btn').disable(true);
                $('#import_wallet_btn').disable(true);
                $('#container').hide();
                $('#progress_header').html(header);
                $('#progress').show();
            }
            
            function show_wallet_info(info_json){
                var wallet_info = $.parseJSON(info_json);
                $('#wallet_address').val(wallet_info['address']);
                $('#wallet_seed_words').val(wallet_info['seed']);
                $('#wallet_viewkey').val(wallet_info['view_key']);
                $('#balance').html(wallet_info['balance']);
                $('#unlocked_balance').html(wallet_info['unlocked_balance']);
                
                $('#progress').hide();
                $('#container').show();
                $('#main_page').hide();
                $('#wallet_info').show();
            }
            
            function close_dialog(){
                app_hub.close_new_wallet_dialog();
                return false;
            }
            
            function reset_ui(){
                $('#gen_wallet_btn').disable(false);
                $('#restore_wallet_btn').disable(false);
                $('#import_wallet_btn').disable(false);
                $('#progress').hide();
                $('#container').show();
                $('#main_page').show();
                $('#wallet_info').hide();
            }
            
            function update_processed_block_height(height, target_height){
                var html = height;
                if(target_height > 0 && target_height > height){
                    sync_pct = target_height > 0 ? (height*100.0/target_height).toFixed(1) : 0;
                    html = height + "/" + target_height + " (" + sync_pct + "%)";
                }
                $('#processed_block_height').html(html);
            }
            
            function paste_seed(){
                app_hub.paste_seed_words();
                return false;
            }
            
            function copy_seed(){
                app_hub.copy_seed($('#wallet_seed_words').val());
                return false;
            }
            
        </script>
        <link href="./css/bootstrap.min.css" rel="stylesheet">
        <link href="./css/font-awesome.min.css" rel="stylesheet">
        <style type="text/css">
            * {
                -webkit-box-sizing: border-box;
                -moz-box-sizing: border-box;
                box-sizing: border-box;
            }
            
            body {
                /* Disable text selection */
                -webkit-user-select: none;  /* webkit all */
                user-select: none;          /* regular */
              
                cursor: default;
                background-color: #666;
                color: #76A500;
                background-position: center center;
                font-family: "Helvetica Neue",Helvetica,Arial,sans-serif;
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
            
            
                        
            table {
                border-spacing: 0;
                border-collapse: collapse;
                font-size: 90%;
            }
            
            
            table thead tr{
                height: 4.5em;
            }
            
            table tbody tr {
                color: #aaa;
                height: 6em;
                line-height: 1.6em;
                border-top: 1px solid #aaa;
            }
            
            table thead tr th{
                text-align: center;
                border-bottom: 1px solid #aaa;
                text-size: 18px;
                padding: auto 1em;
            }
            
            table tr td {
                text-align: center;
            }
            
            .row {
                margin: 5px;
            }
            .row .col-sm-12 {
                background: #fff;
                padding: 10px 30px;
            }
            
            input[type="file"] {
                display: inline-block;
                visibility: hidden;
            }
            .custom-file-upload {
                border: 1px solid #ccc;
                display: inline-block;
                padding: 6px 12px;
                cursor: pointer;
            }
            
            .centered {
              position: fixed;
              width: 730px;
              top: 25%;
              left: 5%;
              text-align: center;
              /* bring your own prefixes */
              transform: translate(-50%, -50%);
            }
            
            #progress {
                background:#fff;
                width:800px;
                height:550px;
                margin: 5px;
                text-align:center;
                display:none;
            }
            
            .form-control.address-box{
                font-family: Menlo, Monaco, Consolas, "Courier New", monospace;
                font-size: 85%;
                /*color: #c7254e;*/
                color: #000;
            }
            
            .container{
                padding: 0;
                width: 100%;
            }
            
            textarea{
                border:none;
                width:100%;
                resize:none;
                font-weight:bold;
            }
            
            .form-group h5 i{
                color: #76A500;
                font-style: normal;
            }
        </style>
    </head>
    <body>
    <div id="container" class="container">
        <form>
            <div id="main_page" style="display:block">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="form-group">
                            <h4>New Wallet</h4>
                            <label for="gen_wallet_btn" class="sr-only">New wallet</label>
                            <button id="gen_wallet_btn" type="button" class="btn btn-primary" onclick="create_new_wallet()"><i class="fa fa-file"></i> Create</button>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12">
                        <h4>Restore Wallet <small></small></h4>
                        <div class="form-group">
                            <label for="seed" style="font-weight: bold;margin-right: 20px">Mnemonic Seed:</label>    <button id="paste_seed_btn" type="button" class="btn btn-warning btn-sm" style="text-transform: none" onclick="paste_seed()"><i class="fa fa-paste"></i> Paste</button>
                            <textarea id="seed" class="form-control" placeholder="Paste 26 mnemonic seed words here (use [Paste] button above or press Ctrl+V)" style="height:80px;margin-bottom:10px;margin-top:10px;font-size:100%"></textarea>
                            <button id="restore_wallet_btn" type="button" class="btn btn-primary" onclick="restore_wallet()"><i class="fa fa-undo"></i> Restore</button>
                            <input id="restore_height_txt" type="text" class="form-control" style="display: inline-block; float:right; width: 100px" value="0"/> <label for="restore_height_txt" style="font-weight: bold; display:inline-block; float:right; margin-right:20px;">Restore from height#</label> 
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12">
                        <div class="form-group">
                            <h4>Import From Existing Wallet</h4>
                            <button id="import_wallet_btn" type="button" class="btn btn-primary" onclick="import_wallet()"><i class="fa fa-cloud-upload"></i> Import</button>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12" style="background: transparent; text-align: center;">
                        <button id="btn_cancel" type="button" class="btn btn-danger center" onclick="close_dialog()"><i class="fa fa-close"></i> Cancel</button>
                    </div>
                </div>
            </div>
            <div id="wallet_info" style="display: none">
                <div class="row">
                    <div class="col-sm-12">
                        <div class="alert alert-success" role="alert"><strong>Wallet was successfully created/restored or imported!</strong></div>
                        <h4 style="margin-bottom:0">Wallet Information</h4>
                    </div>
                    <div class="col-sm-12">
                        <div class="form-group">
                            <label for="wallet_address">Address</label>
                            <input id="wallet_address" type="text" class="form-control address-box" style="color:#c7254e;" readonly="readonly" value="Sumoo..."/>
                        </div>
                        <div class="form-group">
                            <label for="wallet_seed_words">Mnemonic seed <code style="font-weight: bold; color: red">(Important! Always backup the seed words for wallet recovery!)</code></label>
                            <button id="copy_seed_btn" type="button" class="btn btn-warning btn-sm" style="text-transform: none" onclick="copy_seed()"><i class="fa fa-copy"></i> Copy Seed Words</button>
                            <textarea id="wallet_seed_words" class="form-control address-box" style="height:70px;font-size:95%;color:#333" readonly="readonly"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="wallet_viewkey">View key (private)</label>
                            <input id="wallet_viewkey" class="form-control address-box" type="text" readonly="readonly" />
                        </div>
                        <div class="form-group">
                            <h5><i>Balance:</i> <span id="balance">0.000000000</span></h5>
                            <h5><i>Unlocked Balance:</i> <span id="unlocked_balance">0.000000000</span></h5>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-sm-12" style="background: transparent; text-align: center;">
                        <button id="btn_open_wallet" type="button" class="btn btn-success" onclick="close_dialog()">Open Wallet &rsaquo;&rsaquo;</button>
                    </div>
                </div>
            </div>
        </form>
    </div>
    <div id="progress">
        <div class="centered">
            <h3 id="progress_header">Creating/Restoring wallet...</h3>
            <h5 id="processing_block">Processing block#: <code id="processed_block_height">0</code></h5><br/><br/>
            <!--<img src="./images/ajax-loader2.gif" />-->
            <i class="fa fa-refresh fa-spin fa-3x fa-fw"></i>
        </div>
    </div>
    </body>
</html>
"""