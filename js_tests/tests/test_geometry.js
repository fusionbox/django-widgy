var test = require('./setup').test,
   requirejs = require('requirejs'),
   assert = require('chai').assert;

var geometry = requirejs('geometry');


describe('calculateDistance', function() {
 var box = {
   top: 1,
   left: 1,
   right: 3,
   bottom: 3
 };
 it('knows when we are inside', function() {
   assert.equal(geometry.calculateDistance(box, 1, 1), 0);
   assert.equal(geometry.calculateDistance(box, 2, 2), 0);
   assert.equal(geometry.calculateDistance(box, 3, 3), 0);
   assert.equal(geometry.calculateDistance(box, 3, 2), 0);
 });

 it('works outside', function() {
   assert.equal(geometry.calculateDistance(box, 0, 0), 2);
   assert.equal(geometry.calculateDistance(box, 4, 4), 2);
   assert.equal(geometry.calculateDistance(box, 5, 2), 4);
   assert.equal(geometry.calculateDistance(box, 0, 2), 1);
   assert.equal(geometry.calculateDistance(box, 4, 2), 1);
   assert.equal(geometry.calculateDistance(box, 2, 0), 1);
   assert.equal(geometry.calculateDistance(box, 2, 4), 1);
 });
});

describe('rectanglesOverlap', function() {
  it('overlap', function() {
    assert.ok(geometry.rectanglesOverlap({top: 1, left: 1, right: 2, bottom: 2},
                                         {top: 1, left: 1, right: 2, bottom: 2}));
  });
  it('left>right', function() {
    assert.ok(!geometry.rectanglesOverlap({top: 2, left: 2, right: 3, bottom: 3},
                                          {top: 2, left: 1, right: 1, bottom: 3}));
  });
  it('left=right', function() {
    assert.ok(geometry.rectanglesOverlap({top: 2, left: 2, right: 3, bottom: 3},
                                         {top: 2, left: 1, right: 2, bottom: 3}));
  });
  it('right<left', function() {
    assert.ok(!geometry.rectanglesOverlap({top: 2, left: 2, right: 3, bottom: 3},
                                          {top: 2, left: 4, right: 5, bottom: 3}));
  });
  it('right=left', function() {
    assert.ok(geometry.rectanglesOverlap({top: 2, left: 2, right: 3, bottom: 3},
                                         {top: 2, left: 3, right: 5, bottom: 3}));
  });
  it('top>bottom', function() {
    assert.ok(!geometry.rectanglesOverlap({top: 2, left: 1, right: 2, bottom: 3},
                                          {top: 0, left: 1, right: 2, bottom: 1}));
  });
  it('top=bottom', function() {
    assert.ok(geometry.rectanglesOverlap({top: 2, left: 1, right: 2, bottom: 3},
                                         {top: 0, left: 1, right: 2, bottom: 2}));
  });
  it('bottom<top', function() {
    assert.ok(!geometry.rectanglesOverlap({top: 1, left: 1, right: 2, bottom: 2},
                                          {top: 3, left: 1, right: 2, bottom: 4}));
  });
  it('bottom=top', function() {
    assert.ok(geometry.rectanglesOverlap({top: 1, left: 1, right: 2, bottom: 2},
                                         {top: 2, left: 1, right: 2, bottom: 4}));
  });
});
