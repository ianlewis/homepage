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
});
