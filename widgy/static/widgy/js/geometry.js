define([], function() {
  return {
    /**
     * Returns the square of the distance between the point (px, py) and any
     * point in the rectangle bb (zero if the point is inside)
     */
    calculateDistance: function (bb, px, py) {
      var dx, dy;
      dy = Math.max(Math.max(bb.top - py, py - bb.bottom), 0);
      dx = Math.max(Math.max(bb.left - px, px - bb.right), 0);
      return dx * dx + dy * dy;
    },

    /**
     * Do the rectangles described by bb and obb overlap? The rectangles should
     * be in the format returned by Element.getBoundingClientRect.
     */
    rectanglesOverlap: function(bb, obb) {
      return (
        bb.left <= obb.right && bb.right >= obb.left &&
        bb.top <= obb.bottom && bb.bottom >= obb.top
      );
    }
  };
});
