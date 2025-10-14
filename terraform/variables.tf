variable "region" {
  description = "AWS region to deploy resources"
  type = string
  default = "us-east-1"
}


variable "project_tags" {
    description = "Tags to apply to all resources"
    type = map(string)
    default = {
    Project = "AI-Meeting-Assistant"
    Owner = "Aditi-Vakeel"
 }
}