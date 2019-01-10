function formateMemeItem(meme) {
  if (!meme.element) { return meme.text; }

  var $meme = $('<div>').addClass('meme');
  var memeUrl = $(meme.element).attr('data-url');
  $meme.append($('<img height="50" src="' + memeUrl + '" />'));
  $meme.append($('<span class="meme-text">' + meme.text + '</span>'));

  return $meme;
};

function generateMeme() {
  var key = $('.js-meme-selector').val();
  var top = $('#meme-line-1').val();
  var bottom = $('#meme-line-2').val();
  var masked = $('#meme-masked-checkbox').prop('checked');

  var url = "/api/templates/" + key;
  var data = {"top": top, "bottom": bottom, "redirect": false, "masked" : masked};

  $.post(url, data, function(data){
    $("#meme-image").attr('src', data.href + '?watermark=none');
  });
}

function getShareLink() {
  return $("#meme-image").attr('src') + "&share=true";
}

/*** Events ***/

$('.js-meme-selector').select2({
  templateResult: formateMemeItem,
  templateSelection: formateMemeItem
});

$('.js-meme-selector').on('change', function() {
  var link = $(".js-meme-selector option:checked").data('link');
  if (link) {
    var pieces = link.split('/');
    $('#meme-line-1').val(pieces[2]);
    $('#meme-line-2').val(pieces[3]);
  }
  generateMeme();
});

$('#meme-form').on('submit', function(event) {
  event.preventDefault();
  generateMeme();

});

$('#btn-share').on('click', function(event) {
  window.location.href = getShareLink();
});

/*** Loading ***/

$('img').on('load', function(){
  $(this).css('background-image', 'none');
});
