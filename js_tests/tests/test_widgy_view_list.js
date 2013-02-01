var requirejs, expect, test;
test = require('./setup').test;
requirejs = require('requirejs')
assert = require('chai').assert;

describe('Widgy ViewLists', function(){

  beforeEach(function(done){
    var _this = this;
    test.create();
    requirejs([ 'jquery', 'widgy.backbone', 'backbone' ], function(
    $,
    WidgyBackbone,
    Backbone){
      var WidgyViewList;
      Backbone.$ = $;
      WidgyViewList = WidgyBackbone.ViewList;
      _this.WidgyView = WidgyBackbone.View;
      _this.ViewList = new WidgyViewList();
      done();
    });
  });

  afterEach(function(){
    test.destroy();
  });

  it('should push views onto the list property', function(){
    var view = new this.WidgyView();
    this.ViewList.push(view);
  });

});
