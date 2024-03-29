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
        formData: function(e) {
            var watermark = $('#watermark-checkbox').prop("checked");
            return [{name: 'watermark', value: watermark}];
        },
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                //$('<img>').attr("src", file.url).appendTo($('.main'));
                $('<li></li>').text(file.name).appendTo($('#uploaded_list'));
                old_val = $('#img_list').val();
                if (old_val === "") {
                    new_val = file.name + "&rating=" + file.rating;
                } else {
                    new_val = old_val + ";" + file.name + "&rating=" + file.rating;
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
        formData: function(e) {
            var watermark = $('#watermark-checkbox').prop("checked");
            return [{name: 'watermark', value: watermark}];
        },
        done: function (e, data) {
            $.each(data.result.files, function (index, file) {
                $.post(".", {img_name: file.name, img_rating: file.rating}, function(data){
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

    $("#filename-copy").click(function(){
        var to_copy = document.location.protocol + "//" + document.location.host;
        if (document.location.pathname.startsWith("/admin/")) {
            to_copy += document.location.pathname.substring(6);
        } else {
            to_copy += document.location.pathname;
        }
        navigator.clipboard.writeText(to_copy).then(() => {
            $('#copy-confirm').show();
            $('#copy-confirm').fadeOut(2000);
        },() => { alert("Error copying to clipboard"); });
    });

    if ($("#public_link").index !== -1) {
        $("#public_link").val(
            document.location.protocol + "//" + document.location.host +
            "/" + $("#public_link").data('link') + "/"
        );
        $("#public_link").click(function(){
            $(this).focus();
            $(this).select();
            document.execCommand('copy');
            $('#copy-confirm').show();
            $('#copy-confirm').fadeOut(2000);
        });
    }

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
                    $("header .right").addClass("shake");
                    setTimeout(function(){
                        $("#yes-btn").removeClass("shake");
                        $("header .right").removeClass("shake");
                    }, 400);
                } else {
                    alert("Error! " + d.responseJSON.error);
                }
            },
        });
    });

    $("#yes-edited-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "yes_edited"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                if (d.responseJSON.error === "too_many") {
                    $("#yes-edited-btn").addClass("disabled").css("cursor", "not-allowed");
                    $("#yes-edited-btn").addClass("shake");
                    $("header .right").addClass("shake");
                    setTimeout(function(){
                        $("#yes-edited-btn").removeClass("shake");
                        $("header .right").removeClass("shake");
                    }, 400);
                } else {
                    alert("Error! " + d.responseJSON.error);
                }
            },
        });
    });

    $("#yes-unedited-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "yes_unedited"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                if (d.responseJSON.error === "too_many") {
                    $("#yes-unedited-btn").addClass("disabled").css("cursor", "not-allowed");
                    $("#yes-unedited-btn").addClass("shake");
                    $("header .right ").addClass("shake");
                    setTimeout(function(){
                        $("#yes-unedited-btn").removeClass("shake");
                        $("header .right").removeClass("shake");
                    }, 400);
                } else {
                    alert("Error! " + d.responseJSON.error);
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
                alert("Error! " + d.responseJSON.error);
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
                    alert("Error! " + d.responseJSON.error);
                },
            });
        }
    });

    $("#delete-rating-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "none"},
            type: "post",
            success: function(d){
                window.location.reload();
            },
            error: function(d){
                alert("Error! " + d.responseJSON.error);
            },
        });
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
                alert("Error! " + d.responseJSON.error);
            },
        });
    });

    $("#filter-yes").click(function(e){
        if ($("#filter-yes").hasClass("disabled")) {
            $("#filter-yes").removeClass("disabled");
            $("#filter-yes").html(createIcon("show", "16"));
            $(".border.green").parent().css("display", "inline-block");
            $(".border.turquoise").parent().css("display", "inline-block");
        } else {
            $("#filter-yes").addClass("disabled");
            $("#filter-yes").html(createIcon("hide", "16"));
            $(".border.green").parent().css("display", "none");
            $(".border.turquoise").parent().css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-unsafe").click(function(e){
        if ($("#filter-unsafe").hasClass("disabled")) {
            $("#filter-unsafe").removeClass("disabled");
            $("#filter-unsafe").html(createIcon("show", "16"));
            $(".border.yellow").parent().css("display", "inline-block");
        } else {
            $("#filter-unsafe").addClass("disabled");
            $("#filter-unsafe").html(createIcon("hide", "16"));
            $(".border.yellow").parent().css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-no").click(function(e){
        if ($("#filter-no").hasClass("disabled")) {
            $("#filter-no").removeClass("disabled");
            $("#filter-no").html(createIcon("show", "16"));
            $(".border.red").parent().css("display", "inline-block");
        } else {
            $("#filter-no").addClass("disabled");
            $("#filter-no").html(createIcon("hide", "16"));
            $(".border.red").parent().css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-all").click(function(e){
        const trans_all = $("#filter-all").data("transAll"),
              trans_rated = $("#filter-all").data("transRated"),
              trans_not_rated = $("#filter-all").data("transNotRated");
        if ($("#filter-all").hasClass("disabled")) {
            // Filtering status
            if ($("#filter-all").data("status") === "not-rated") {
                // Not-Rated -> Rated
                $("#filter-all").text(trans_rated).data("status", "rated");
                $(".pic-grid-item a").css("display", "inline-block"); // Show all
                // And then hide all without rating-border
                $(".pic-grid-item a img:not(.border)").parent().css("display", "none");
            } else if ($("#filter-all").data("status") === "rated") {
                // Rated -> All
                $("#filter-all").removeClass("disabled");
                $("#filter-all").text(trans_all).data("status", "all");
                $(".pic-grid-item a").css("display", "inline-block"); // Show all
            }
        } else {
            // Initial status / All -> Not-Rated
            $("#filter-all").addClass("disabled");
            $("#filter-all").text(trans_not_rated).data("status", "not-rated");
            $(".border").parent().css("display", "none"); // Hide all with rating-border
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });

     $("#unedited_checkbox").click(function(e){
        if ($('#unedited_checkbox').prop('checked')) {
            $('#max_unedited_count').removeClass('hidden');
        } else {
            $('#max_unedited_count').addClass('hidden');
        }
     });

    $('#star-none-btn').click(function(e){
        $.ajax(".", {
            data: {rating: "/"},
            type: "post",
            success: function(d){
                window.location.reload(false);
            },
            error: function(d){
                alert("Error! " + d.responseJSON.error);
            },
        });
    });

    $('#star-zero-btn').click(function(e){
        $.ajax(".", {
            data: {rating: "0"},
            type: "post",
            success: function(d){
                window.location.reload(false);
            },
            error: function(d){
                alert("Error! " + d.responseJSON.error);
            },
        });
    });

    $('#star-half-btn').click(function(e){
        $.ajax(".", {
            data: {rating: "1"},
            type: "post",
            success: function(d){
                window.location.reload(false);
            },
            error: function(d){
                alert("Error! " + d.responseJSON.error);
            },
        });
    });

    $('#star-full-btn').click(function(e){
        $.ajax(".", {
            data: {rating: "2"},
            type: "post",
            success: function(d){
                window.location.reload(false);
            },
            error: function(d){
                alert("Error! " + d.responseJSON.error);
            },
        });
    });

    function createIcon(icon, size) {
        return '<svg class="genericons-neue genericons-neue-hide" width="' + size + 'px" height="' + size + 'px"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="/static/genericons-neue.svg#' + icon + '"></use></svg>';
    }
});