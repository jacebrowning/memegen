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
  var top = $('#meme-text-top').val();
  var bottom = $('#meme-text-bottom').val();

  var url = "/api/templates/" + key;
  var data = {"top": top, "bottom": bottom, "redirect": false};

  $.post(url, data, function(data){
    $("#meme-image img").attr('src', data.href);
    $("#meme-image").attr('href', data.href);
  });
}

function getShareLink() {
  return $("#meme-image").attr('href') + "?share=true";
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
    $('#meme-text-top').val(pieces[2]);
    $('#meme-text-bottom').val(pieces[3]);
  }
  generateMeme();
});

$('#meme-form').on('submit', function(event) {
  event.preventDefault();
  generateMeme();

});

var clipboard = new Clipboard('#btn-copy', {
  text: function(trigger) {
    return getShareLink();
  }
});
clipboard.on('success', function(event) {
  $(event.trigger).attr('title', 'Link Copied').tooltip('fixTitle').tooltip('show');
});
clipboard.on('error', function(event) {
  console.log(event);
});

$('#btn-share').on('click', function(event) {
  var url = getShareLink();
  var win = window.open(url, '_blank');
  if (win) {
    win.focus();
  } else {
    window.location.href = url;
  }
});

/*** Loading ***/

$('img').on('load', function(){
  $(this).css('background-image', 'none');
});
