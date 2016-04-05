$(document).ready(function(){
    $.getJSON("/api/snapshot_overall_info").success(function(data){
        $("div#overall_info").html(data);
    });
    
    $.getJSON("/api/snapshot_detail_info").success(function(data){
        $("div#detail_info").html(data);
    });

    $("#refresh").click(function(){
        $("#refresh").prop("disabled", true);
        $.getJSON("/api/reload_snapshot").success(function(json){
            $("img#snapshot").prop("src", "/static/temp/snapshot.jpg?" + Math.random());
            $("div#overall_info").html(json.snapshot_overall_info);
            $("div#detail_info").html(json.snapshot_detail_info);
            $("#refresh").prop("disabled", false);
        });
    });
})