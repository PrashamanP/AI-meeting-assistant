output "meeting_uploads_bucket" {
  value = data.aws_s3_bucket.meeting_uploads.bucket
}

output "meeting_transcripts_bucket" {
  value = data.aws_s3_bucket.meeting_transcripts.bucket
}

output "meeting_summaries_bucket" {
  value = data.aws_s3_bucket.meeting_summaries.bucket
}

output "meeting_embeddings_bucket" {
  value = data.aws_s3_bucket.meeting_embeddings.bucket
}
