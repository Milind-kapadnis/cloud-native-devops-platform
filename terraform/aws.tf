provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project   = "cloud-native-devops-platform"
      ManagedBy = "terraform"
    }
  }
}
