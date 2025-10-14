data  "aws_s3_bucket" "meeting_uploads" {
  bucket = "aima-meeting-uploads"
}

data  "aws_s3_bucket" "meeting_transcripts" {
  bucket = "aima-meeting-transcripts"
}

data  "aws_s3_bucket" "meeting_summaries" {
  bucket = "aima-meeting-summaries"
}

data  "aws_s3_bucket" "meeting_embeddings" {
  bucket = "aima-meeting-embeddings"
}
