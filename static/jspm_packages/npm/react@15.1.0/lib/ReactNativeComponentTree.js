/* */ 
(function(process) {
  'use strict';
  var invariant = require('fbjs/lib/invariant');
  var instanceCache = {};
  function getRenderedNativeOrTextFromComponent(component) {
    var rendered;
    while (rendered = component._renderedComponent) {
      component = rendered;
    }
    return component;
  }
  function precacheNode(inst, tag) {
    var nativeInst = getRenderedNativeOrTextFromComponent(inst);
    instanceCache[tag] = nativeInst;
  }
  function uncacheNode(inst) {
    var tag = inst._rootNodeID;
    if (tag) {
      delete instanceCache[tag];
    }
  }
  function getInstanceFromTag(tag) {
    return instanceCache[tag] || null;
  }
  function getTagFromInstance(inst) {
    !inst._rootNodeID ? process.env.NODE_ENV !== 'production' ? invariant(false, 'All native instances should have a tag.') : invariant(false) : void 0;
    return inst._rootNodeID;
  }
  var ReactNativeComponentTree = {
    getClosestInstanceFromNode: getInstanceFromTag,
    getInstanceFromNode: getInstanceFromTag,
    getNodeFromInstance: getTagFromInstance,
    precacheNode: precacheNode,
    uncacheNode: uncacheNode
  };
  module.exports = ReactNativeComponentTree;
})(require('process'));
