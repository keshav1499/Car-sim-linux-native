group "default" {
  targets = ["ecu", "validation"]
}

target "ecu" {
  context = "."
  dockerfile = "ecu/Dockerfile"
  tags = ["car-sim-linux-native-ecu"]
}

target "validation" {
  context = "."
  dockerfile = "validation/Dockerfile"
  tags = ["car-sim-linux-native-validation"]
}
