$(function() {
  $('.blog-post').each(function() {
    $(this).find("a[rel*=lightbox]").lightBox({
      imageLoading: '/static/img/lightbox/lightbox-ico-loading.gif',
      imageBtnClose: '/static/img/lightbox/lightbox-btn-close.gif',
      imageBtnPrev: '/static/img/lightbox/lightbox-btn-prev.gif',
      imageBtnNext: '/static/img/lightbox/lightbox-btn-next.gif',
      imageBlank: '/static/img/lightbox/lightbox-blank.gif'
    });
  });
});
