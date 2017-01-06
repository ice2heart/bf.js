module.exports   = function(statement){
  if (statement){
    console.log("Test is OK");
    return;
  }
  console.log("Test is Failed");
  throw 'Error state';
};
