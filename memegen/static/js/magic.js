$("#btn-generate").on('click', function(e) {
  var memeText = $('#meme-text').val();
  var magicUrl = "/api/magic/" + memeText;

  $.get(magicUrl, function(data) {
    console.log(data);
    if (!data[0]) return;

    var linkUrl = data[0].link;
    $.get(linkUrl, function(data) {
      console.log(data);
      var imageUrl = data.direct.visible;

      $("#meme-image img").attr('src', imageUrl);
      $("#meme-image").attr('href', imageUrl)
    });

  });

});
