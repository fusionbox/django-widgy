;(function() {


  var Bucket = Widgy.contents.Bucket = Widgy.contents.ContentModel.extend({
    viewClass: 'BucketView'
  });


  var BucketView = Widgy.nodes.BucketView = Widgy.nodes.NodeView.extend({
    tagName: 'section',
    className: 'bucket',

    template: 'bucket'
  });
})();
