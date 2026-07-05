variable "aws_region" {
  description = "Región de AWS (fija en us-east-1 para AWS Academy)"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "Perfil de AWS CLI a usar"
  type        = string
  default     = "academy"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nombre del key pair existente en AWS (provisto por el lab)"
  type        = string
  default     = "vockey"
}

variable "instance_profile_name" {
  description = "Instance profile existente del lab (no se crea uno nuevo)"
  type        = string
  default     = "LabInstanceProfile"
}

variable "ssh_allowed_cidr" {
  description = "CIDR permitido para conectarse por SSH (usa tu IP/32, no dejes 0.0.0.0/0 en algo real)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "root_volume_size_gb" {
  description = "Tamaño del disco raíz en GB (ahí vive la base de datos de n8n). El snapshot base de Amazon Linux 2023 exige mínimo 30GB."
  type        = number
  default     = 30
}

variable "repo_url" {
  description = "URL del repo git a clonar en la instancia"
  type        = string
  default     = "https://github.com/Cristofer-SanMartin-Dev/Trato_Hecho.git"
}

variable "project_name" {
  description = "Prefijo de nombre para los recursos"
  type        = string
  default     = "trato-hecho"
}

# ── Secretos: NO tienen default. Se pasan vía terraform.tfvars ──
# (terraform.tfvars está en .gitignore, nunca se sube al repo)
variable "supabase_url" {
  description = "URL del proyecto Supabase"
  type        = string
  sensitive   = true
}

variable "supabase_key" {
  description = "API key (anon) de Supabase"
  type        = string
  sensitive   = true
}

variable "mercadopago_access_token" {
  description = "Access token de MercadoPago (TEST- o APP_USR-)"
  type        = string
  sensitive   = true
}
