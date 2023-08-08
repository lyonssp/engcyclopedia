provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "scrape_data" {
  bucket = "engcyclopedia-scrape-data"
}
