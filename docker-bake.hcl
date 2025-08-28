group "default" {
  targets = ["ecu", "validation", "infotainment"]
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

target "infotainment" {
  context = "."
  dockerfile = "infotainment/Dockerfile"
  tags = ["car-sim-linux-native-infotainment"]
}
