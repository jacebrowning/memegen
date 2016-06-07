function encodeMemeText(str) {
  return str
    .replace(/-/g, '--')
    .replace(/_/g, '__')
    .replace(/\?/g, '~q')
    .replace(/%/g, '~p')
    .replace(/#/g, '~h')
    .replace(/\//g, '~s')
    .replace(/\s+/g, '-') || '_';
}

function decodeMemeText(str) {
  return str
    .replace(/-/g, ' ')
    .replace(/_/g, '')
    .replace(/~q/g, '?')
    .replace(/~p/g, '%')
    .replace(/~h/g, '#')
    .replace(/~s/g, '/')
}

function encodeMemeURL(url) {
  var encodedURL = encodeURI(url);
  return encodedURL.replace(/,/g, '%2C').replace(/'/g, '%27');
}

function formateMemeItem(meme) {
  if (!meme.element) { return meme.text; }

  var $meme = $('<div>').addClass('meme');
  var memeUrl = encodeMemeURL($(meme.element).attr('data-url'));
  $meme.append($('<img height="50" src="' + memeUrl + '" />'));
  $meme.append($('<span class="meme-text">' + meme.text + '</span>'));

  return $meme;
};

function generateMeme() {
  var memeId = $('.js-meme-selector').val();
  var memeTextTop = encodeMemeText($('#meme-text-top').val());
  var memeTextBottom = encodeMemeText($('#meme-text-bottom').val());
  if (memeId && memeTextTop && memeTextBottom) {
    var url = '/' + memeId + '/' + memeTextTop + '/' + memeTextBottom;
    $("#meme-link").attr('href', url);
    $("#meme-link").text(url);
    $("#meme-image img").attr('src', encodeURI(url).replace(/,/g, '%2C').replace(/'/g, '%27') + '.jpg');
    $("#meme-image").attr('href', encodeURI(url).replace(/,/g, '%2C').replace(/'/g, '%27') + '.jpg');
  }
}

/*** Events ****/
$('.js-meme-selector').select2({
  templateResult: formateMemeItem,
  templateSelection: formateMemeItem
});

$( ".js-meme-selector" ).on('change', function() {
  var link = $( ".js-meme-selector option:checked").data('link');
  if (link) {
    var pieces = link.split('/');
    $('#meme-text-top').val(decodeMemeText(pieces[2]));
    $('#meme-text-bottom').val(decodeMemeText(pieces[3]));
  }
  generateMeme();
});

$("#btn-generate").on('click', function(e) {
  generateMeme();
});

if ($('#meme-text-top').val() || $('#meme-text-bottom').val()) {
  $(".js-meme-selector").trigger("change");
}
