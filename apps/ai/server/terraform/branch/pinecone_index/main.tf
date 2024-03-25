terraform {
  required_providers {
    pinecone = {
      source  = "skyscrapr/pinecone"
      version = "0.5.1"
    }
  }
}

resource "pinecone_index" "my_index" {
  name      = var.index_name
  dimension = 1536
  metric    = "cosine"
  spec = {
    serverless = {
      cloud  = "aws"
      region = "us-west-2"
    }
  }
}
