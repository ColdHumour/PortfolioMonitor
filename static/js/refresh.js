function load_info(){
    $.get("/api/snapshot_overall_info").success(function(data){
        $("div#overall_info").html(data);
    });
    
    $.get("/api/snapshot_detail_info").success(function(data){
        $("div#detail_info").html(data);
    });
}

function reload_snapshot_img(){
    $("img#snapshot").prop("src", "/static/temp/snapshot.jpg?" + Math.random());
}

function reload_snapshot(){
    $.getJSON("/api/reload_snapshot").success(function(json){
        reload_snapshot_img();
        $("div#overall_info").html(json.snapshot_overall_info);
        $("div#detail_info").html(json.snapshot_detail_info);
        $("button#refresh").prop("disabled", false);
    });
}

$(document).ready(function(){
    load_info();

    $("div#detail_edit").hide()
    $("div#detail_edit_control").hide()

    $.get("/api/latest_position_string").success(function(data){
        $("textarea#pos_string").val(data);
    });

    $("button#refresh").click(function(){
        $("button#refresh").prop("disabled", true);
        reload_snapshot();
    });

    $("input#is_auto_refresh").bind("click", function(){
        if ($(this).prop("checked") == true) {
            $("button#refresh").prop("disabled", true)
        } else {
            $("button#refresh").prop("disabled", false)
        }
    });

    $("button#edit").click(function(){
        $("div#detail_info").hide();
        $("div#detail_info_control").hide();
        $("div#detail_edit").show();
        $("div#detail_edit_control").show();
    });    

    $("button#submit").click(function(){
        $.ajax({
            url: '/api/update_position',
            type: 'PUT',
            data: {pos_string: $("textarea#pos_string").val()},
            success: function(){
                reload_snapshot_img();
                load_info();
            }
        });
        $("div#detail_info").show();
        $("div#detail_info_control").show();
        $("div#detail_edit").hide();
        $("div#detail_edit_control").hide();
    });

    $("button#cancel").click(function(){
        $.getJSON("/api/latest_position_string").success(function(data){
            $("textarea#pos_string").val(data);
        });
        $("div#detail_info").show();
        $("div#detail_info_control").show();
        $("div#detail_edit").hide();
        $("div#detail_edit_control").hide();
    });

    $("button#save").click(function(){
        var date = new Date()
        var now = date.toLocaleString()
        if (date.getHours() >= 15) {
            $.get("/api/save");
            $("div#state").html("<p>保存于 " + new Date().toLocaleString() + "</p>")
        } else {
            $("div#state").html("<p>需要等到15:00以后才能保存</p>")
        }
    });
})