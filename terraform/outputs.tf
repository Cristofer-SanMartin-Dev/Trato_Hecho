output "public_ip" {
  description = "IP pública fija de la instancia"
  value       = aws_eip.app.public_ip
}

output "instance_id" {
  value = aws_instance.app.id
}

output "webhook_url" {
  description = "URL del webhook de n8n para pegar en config.js"
  value       = "http://${aws_eip.app.public_ip}:5678/webhook/chat-v2"
}

output "frontend_url" {
  value = "http://${aws_eip.app.public_ip}:3000"
}

output "n8n_editor_url" {
  value = "http://${aws_eip.app.public_ip}:5678"
}

output "ssh_command" {
  description = "Comando para conectarte por SSH (ajusta la ruta de tu .pem)"
  value       = "ssh -i \"C:\\ruta\\a\\vockey.pem\" ec2-user@${aws_eip.app.public_ip}"
}
