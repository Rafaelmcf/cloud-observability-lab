# ----------------------------------------
# Key pair - a fechadura do servidor
# ----------------------------------------
resource "aws_key_pair" "lab" {
  key_name   = "lab-key"
  public_key = file("~/.ssh/lab-key.pub")
}
