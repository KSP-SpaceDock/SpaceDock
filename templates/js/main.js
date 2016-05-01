{% raw %}
<script language="javascript">

    jQuery.fn.extend({
        aspectratio: function (space=null) {
            var arel = $(this);
            $(arel).each(function (el, index) {
                var ars = $(this).attr("data-aspectratio");
                var arsp = $(this).attr("data-space");
                if (space.isNull) {
                    if (typeof arsp !== typeof undefined && arsp !== false) {

                    } else {
                        var arsp = 0;
                    }
                } else {
                    var arsp = space;
                }
                if (typeof ars !== typeof undefined && ars !== false) {
                    var ar = ars.split('-');
                } else {

                    var ar = Array(16, 9);
                }
                var x = $(this).outerWidth();
                var h = parseInt(((x / ar[0]) * ar[1]) + arsp);
                //h = h.toFixed(0);
                $(this).css('height', h + 'px');
            });
            return;
        }
    });

    //rearanges stuff on mobile
    function screenw(width){

    }
    //set aspect ratio of images
    function setgridaspect() {
        $(".previewbox").aspectratio(40);
        $(".previewbox").css('height', $(".gridmode .modbox:first").outerHeight());
        $(".previewbox .back").aspectratio(40);
        $(".back").aspectratio(0);
        $(".thumbnail").aspectratio(0);
        $(".listthumb").aspectratio(0);

        // $(".tablemode .thumbnail .header-img").aspectratio(0);
    }


$(document).ready(function () {

   //main menu button
    $(".navbtn").click(function (el,index) {
       if($(this).hasClass("navbtnactive")){
           $(this).removeClass("navbtnactive");
           $("nav").hide();
           $(".contentwrap").show();
       } else{
           $(this).addClass("navbtnactive");
           $("nav").show();
           $(".contentwrap").hide();
       }
    });

    //hide nav menu on mobile when item is clicked
    $("nav").click(function(el,index){
       if($(".navbtn").hasClass("navbtnactive")){
           $(this).removeClass("navbtnactive");
           $("nav").hide();
           $(".contentwrap").show();
       }
    });

    //show modals
    $('[data-toggle="modal"]').click(function(el,index){
       $(".modalContent").hide();
       $(".dim").show();
       $($(this).attr("data-target")).show();
    });

    //close modal
    $('[data-dismiss="modal"]').click(function(el,index){
       $(".modalContent").hide();
       $(".dim").hide();
    });

    //tab panel
    $(".tabhtext").click(function(el,index){
       var tabhid = $(this).attr("data-tabhid");
       var tabpanel = $(this).attr("data-tabpanel");
       $(".tabline").show();
       $(".tabdip").hide();
       $(".tabhl" + tabhid).hide();
       $(".tabhd" + tabhid).show();
       $(".tabcontent").removeClass("tabactive");
       $("#" + tabpanel).addClass("tabactive");
    });


    //document resize events
    $(window).resize(function(ha){
        var docw = $(document).innerWidth();


        if(docw > 750) {

            //show invisible navs when docked
            $("nav").removeAttr("style");
                $(".tabhead line").each(function(el,index){

                    var y1= $(this).attr("y1");
                    var y2= $(this).attr("y2");

                    if(y1.length == 4 && y2.length == 4) {
                        ny1 = y1.substr(1,y1.length-1);
                        ny2 = y2.substr(1,y2.length-1);
                        $(this).attr({y1: ny1, y2: ny2});
                    }
                });
        }else if(docw <= 750){

            //reset menu state to before resizing
            if($(".navbtn").hasClass("navbtnactive")){
                $("nav").show();
            }else{
                $("nav").hide();
            }

            if(docw <= 550) {
                $(".tabhead line").each(function(el,index){

                    var y1= $(this).attr("y1");
                    var y2= $(this).attr("y2");

                    if(y1.length == 3 && y2.length == 3) {
                        ny1 = "2" + y1;
                        ny2 = "2" + y2;
                        $(this).attr({y1: ny1, y2: ny2});
                    }
                });
               // $(".tabhead text").each(function(el,index){
                //    var y= $(this).attr("y");
                //    if(y.length == 3 ) {
                //        ny = "2" + y;
                //        $(this).attr({y: ny});
                //    }
                //});



            }
        }


        setgridaspect();

    });



        setgridaspect();



        $(".changer").mouseover(function (el, index) {
            $(this).children(".front").hide();
            $(this).children(".back").show();
            setgridaspect();

        });

        $(".changer").mouseout(function (el, index) {
            $(this).children(".front").show();
            $(this).children(".back").hide();
            setgridaspect();
        });


        // set tab head for mobile
         var docw = $(document).innerWidth();
            if(docw <= 550) {
                $(".tabhead line").each(function (el, index) {

                    var y1 = $(this).attr("y1");
                    var y2 = $(this).attr("y2");

                    if (y1.length == 3 && y2.length == 3) {
                        ny1 = "2" + y1;
                        ny2 = "2" + y2;
                        $(this).attr({y1: ny1, y2: ny2});
                    }
                });
            }
          $(".dropdown").chosen({
            disable_search_threshold: 10,
            no_results_text: "Oops, nothing found!",
            inherit_select_classes: true,
            max_selected_options: 1,
            placeholder_text_multiple: "Select Options...",
            placeholder_text_single: "Select an Option..."

          });
});
</script>
{% endraw %}