function make(arr, el) {
  var i, i_m, item;
  var len = arr.length;
  var res = [];

  for (i = len; i >= 0; i--) {
    res.push(
      ([]).concat(
        arr.slice(0, i), [el],
        arr.slice(i, i_m)
      )
    );
  }

  return res;
}



function combinations(arr) {
  var prev, curr, el, i;
  var len = arr.length;

  curr = [
    [arr[0]]
  ];

  for (i = 1; i < len; i++) {
    el = arr[i];
    prev = curr;
    curr = [];

    for (let item of prev) {
      curr = curr.concat(
        make(item, el)
      );
    }
  }
  return curr;
}

module.exports = combinations;
