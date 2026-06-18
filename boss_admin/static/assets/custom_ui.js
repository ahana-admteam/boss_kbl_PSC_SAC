$(window).on("load", function() {
    $('.container_ani').addClass('box-anim1');
});

$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
    $('#show-hidden-menu').click(function() {
        $('.hidden-menu').slideToggle("slow");
        $('.hidden-menu-branch').hide("slow");
        $('.hidden-menu-notification').hide("slow");

        // Alternative animation for example
        // slideToggle("fast");
      });
      $('#show-hidden-branch-name').click(function() {
        $('.hidden-menu-branch').slideToggle("slow");
        $('.hidden-menu-notification').hide("slow");
        $('.hidden-menu').hide("slow");
      });
      $('#show-hidden-notification').click(function() {
        $('.hidden-menu-notification').slideToggle("slow");
        $('.hidden-menu').hide("slow");
        $('.hidden-menu-branch').hide("slow");

      });
});
