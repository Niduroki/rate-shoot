$(function () {
    var $grid = $(".pic-grid").masonry({
        itemSelector: '.pic-grid-item',
        percentPosition: true
    });
    $grid.imagesLoaded().progress( function() {
        $grid.masonry('layout');
    });
    var $shoot_grid = $(".shoot-grid").masonry({
        itemSelector: '.shoot-grid-item',
        percentPosition: true
    });
    $shoot_grid.imagesLoaded().progress( function() {
        $shoot_grid.masonry('layout');
    });

    $('#fileupload').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                //$('<img>').attr("src", file.url).appendTo($('.main'));
                $('<li></li>').text(file.name).appendTo($('#uploaded_list'));
                old_val = $('#img_list').val();
                if (old_val === "") {
                    new_val = file.name;
                } else {
                    new_val = old_val + ";" + file.name;
                }
                $('#img_list').val(new_val);
            });
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .bar').css(
                'width',
                progress + '%'
            );
        }
    });

    $('#fileupload-overview').fileupload({
        dataType: 'json',
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $.post(".", {img_list: file.name}, function(data){
                    var img_link = "/admin/" + $("#shoot_link_help").val() + "/" + file.name + "/";
                    var img_tag = "<img src='" + file.url + "'>";
                    var new_elem = $("<div class='pic-grid-item pic'><a href='" + img_link + "'>" + img_tag + "</a></div>");
                    $grid.append(new_elem).masonry('appended', new_elem);
                });
            });
        },
        progressall: function (e, data) {
            var progress = parseInt(data.loaded / data.total * 100, 10);
            $('#progress .bar').css(
                'width',
                progress + '%'
            );
        }
    });

    $("#public_link").click(function(){
        $(this).focus();
        $(this).select();
        document.execCommand('copy');
        $('#copy-confirm').show();
        $('#copy-confirm').fadeOut(2000);
    });

    $("#yes-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "yes"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                if (d.responseJSON.error === "too_many") {
                    $("#yes-btn").addClass("disabled").css("cursor", "not-allowed");
                    $("#yes-btn").addClass("shake");
                    $("header .right .small-title").addClass("shake");
                    setTimeout(function(){
                        $("#yes-btn").removeClass("shake");
                        $("header .right .small-title").removeClass("shake");
                    }, 400);
                } else {
                    alert("Fehler! " + d.responseJSON.error);
                }
            },
        });
    });

    $("#no-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "no"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                alert("Fehler! " + d.responseJSON.error);
            },
        });
    });

    $("#unsafe-btn-submit").click(function(e){
        var comment = $('#unsafe-comment').val();
        if (comment !== "") {
            $.ajax(".", {
                data: {rating: "unsafe", comment: comment},
                type: "post",
                success: function(d){
                    window.location = d.next;
                },
                error: function(d){
                    alert("Fehler! " + d.responseJSON.error);
                },
            });
        }
    });

    $("#prune-btn").click(function(e){
        $.post("/admin/prune/", "", function(data){
            console.log(data);
            $("#prune-btn").hide();
            $('#prune-count-1').text(data.count);
            $('#prune-count-2').text(data.count2);
            $("#prune-confirm").show();
        });
    });

    $("#delete-img").click(function(e){
        var href = $("#delete-img").data("target");
        $.ajax(href, {
            type: "delete",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                alert("Fehler! " + d.responseJSON.error);
            },
        });
    });

    $("#filter-yes").click(function(e){
        if ($("#filter-yes").hasClass("disabled")) {
            $("#filter-yes").removeClass("disabled");
            $("#filter-yes").html(createIcon("show", "16"));
            $(".border.green").css("display", "inline-block");
        } else {
            $("#filter-yes").addClass("disabled");
            $("#filter-yes").html(createIcon("hide", "16"));
            $(".border.green").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-unsafe").click(function(e){
        if ($("#filter-unsafe").hasClass("disabled")) {
            $("#filter-unsafe").removeClass("disabled");
            $("#filter-unsafe").html(createIcon("show", "16"));
            $(".border.yellow").css("display", "inline-block");
        } else {
            $("#filter-unsafe").addClass("disabled");
            $("#filter-unsafe").html(createIcon("hide", "16"));
            $(".border.yellow").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-no").click(function(e){
        if ($("#filter-no").hasClass("disabled")) {
            $("#filter-no").removeClass("disabled");
            $("#filter-no").html(createIcon("show", "16"));
            $(".border.red").css("display", "inline-block");
        } else {
            $("#filter-no").addClass("disabled");
            $("#filter-no").html(createIcon("hide", "16"));
            $(".border.red").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-all").click(function(e){
        if ($("#filter-all").hasClass("disabled")) {
            $("#filter-all").removeClass("disabled");
            $("#filter-all").text("Alles");
            $(".border").css("display", "inline-block");
        } else {
            $("#filter-all").addClass("disabled");
            $("#filter-all").text("Unbewertet");
            $(".border").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });

    function createIcon(icon, size) {
        return '<svg class="genericons-neue genericons-neue-hide" width="' + size + 'px" height="' + size + 'px"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/static/genericons-neue.svg#' + icon + '"></use></svg>';
    }
});