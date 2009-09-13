$(function() {
  windows = $('div.jqmWindow');
  if (windows.length) {
    windows.jqm();
    $('a.modal').each(function() {
      $(this).attr('href','javascript:void(0);').click(function() {
        $("#"+$(this).attr('rel')).jqmShow();
      });
    });
    $('a.modal-close').click(function() {
      $("#"+$(this).attr('rel')).jqmHide();
    });
  }

  //Flickr Images
  $("div.lifestream-item-inner.flickr-com img").each(function() {
    var img = $(this);
    var w = img.width();
    var extra = -1 * (w - 214)/2;
    img.css("left", extra+"px");
    // alert($(this).attr("src")+": "+$(this).width());
  });
});
