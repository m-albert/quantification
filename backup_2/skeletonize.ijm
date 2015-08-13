open("/tmp/delme.tif");
run("Skeletonize (2D/3D)");
run("Save", "save=/tmp/delme_out.tif");