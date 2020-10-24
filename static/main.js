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
        $grid.masonry('layout');
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

    $("#yes-btn").click(function(e){
        $.ajax(".", {
            data: {rating: "yes"},
            type: "post",
            success: function(d){
                window.location = d.next;
            },
            error: function(d){
                alert("Fehler! " + d.responseJSON.error);
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
            $(".border.green").css("display", "inline-block");
        } else {
            $("#filter-yes").addClass("disabled");
            $(".border.green").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-unsafe").click(function(e){
        if ($("#filter-unsafe").hasClass("disabled")) {
            $("#filter-unsafe").removeClass("disabled");
            $(".border.yellow").css("display", "inline-block");
        } else {
            $("#filter-unsafe").addClass("disabled");
            $(".border.yellow").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-no").click(function(e){
        if ($("#filter-no").hasClass("disabled")) {
            $("#filter-no").removeClass("disabled");
            $(".border.red").css("display", "inline-block");
        } else {
            $("#filter-no").addClass("disabled");
            $(".border.red").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
    $("#filter-all").click(function(e){
        if ($("#filter-all").hasClass("disabled")) {
            $("#filter-all").removeClass("disabled");
            $(".border").css("display", "inline-block");
        } else {
            $("#filter-all").addClass("disabled");
            $(".border").css("display", "none");
        }
        $grid.imagesLoaded().progress( function() {
            $grid.masonry('layout');
        });
    });
});