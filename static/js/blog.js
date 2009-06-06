$(function() {
  $('.blog-post').each(function() {
    $(this).find("a[rel*=lightbox]").lightBox({
      imageLoading: MEDIA_URL+'img/lightbox/lightbox-ico-loading.gif',
      imageBtnClose: MEDIA_URL+'img/lightbox/lightbox-btn-close.gif',
      imageBtnPrev: MEDIA_URL+'img/lightbox/lightbox-btn-prev.gif',
      imageBtnNext: MEDIA_URL+'img/lightbox/lightbox-btn-next.gif',
      imageBlank: MEDIA_URL+'img/lightbox/lightbox-blank.gif'
    });
  });
});
