var requirejs, expect, test;
var test = require('./setup').test;
var requirejs = require('requirejs')
var assert = require('chai').assert;

describe('Widgy ViewLists', function(){

  beforeEach(function(done){
    var _this = this;
    this.MockView = function(cid){
      this.i_was_closed = false;
      this.off_was_called = false;
      this.on_was_called = true;
      this.cid = cid;
      this.on = function(){this.off_was_called = true;};
      this.off = function(){this.on_was_called = true;};
      this.close = function() { this.i_was_closed = true; };
      this.model = {
        id: cid
      };
    };
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
    var mockview = new this.MockView(1);
    this.ViewList.push(mockview);
    assert.deepEqual(this.ViewList.list, [ mockview ]);
  });


  it('should remove views by view object', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.ViewList.list = [ mockview, mockview1, mockview2 ];
    this.ViewList.remove(mockview2);
    assert.deepEqual(this.ViewList.list, [ mockview, mockview1 ]);
  });


  it('should return false if remove is called and view is not found', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.ViewList.list = [ mockview, mockview1 ];
    assert.isFalse(this.ViewList.remove(mockview2));
  });


  it('should call close on each view in its list when closeAll is used', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.ViewList.list = [ mockview, mockview1, mockview2 ];
    this.ViewList.closeAll();
    assert.isTrue(this.ViewList.list[0].i_was_closed);
    assert.isTrue(this.ViewList.list[1].i_was_closed);
    assert.isTrue(this.ViewList.list[2].i_was_closed);
  });


  it('should find a view object from its model id', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.ViewList.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.ViewList.findById(2), mockview1);
  });


  it('should find a view object from its element', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3),
        search_el = document.createElement('div');
    search_el.setAttribute('id', 'found_me');
    mockview.el = document.createElement('div');
    mockview1.el = search_el;
    mockview2.el = document.createElement('div');

    this.ViewList.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.ViewList.findByEl(search_el), mockview1);
  });

  it('should find a view object from its view model', function(){
    var mockview = new this.MockView(1),
        mockview1 = new this.MockView(2),
        mockview2 = new this.MockView(3);
    this.ViewList.list = [ mockview, mockview1, mockview2 ];
    assert.strictEqual(this.ViewList.findByModel(mockview1.model), mockview1);
  });
});

describe('Spinner View', function(){

  beforeEach(function(done){
    var _this = this;
    test.create();
    requirejs([ 'jquery', 'widgy.backbone', 'backbone' ], function(
    $,
    WidgyBackbone,
    Backbone){
      var WidgyViewList;
      Backbone.$ = $;
      _this.Spinner = WidgyBackbone.Spinner;
      done();
    });
  });

  afterEach(function(){
    test.destroy();
  });

  it('should set the "disabled" property on its element on initialization', function(){
    var spinner = new this.Spinner();
    assert.isTrue(spinner.el.disabled);
  });

  it('should unset the "disabled" property on its element after calling restore', function(){
    var spinner = new this.Spinner();
    spinner.restore();
    assert.isFalse(spinner.el.disabled);
  });

  it('should add a "loading" class to its element on initialization', function(){
    var spinner = new this.Spinner();
    assert.isTrue(spinner.$el.hasClass('loading'));
  });

  it('should remove "loading" class to its element on initialization', function(){
    var spinner = new this.Spinner();
    spinner.restore();
    assert.isFalse(spinner.$el.hasClass('loading'));
  });

});
