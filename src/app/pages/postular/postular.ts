import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { RqService } from '../../services/rq';

@Component({
  selector: 'app-postular',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './postular.html',
  styleUrl: './postular.css'
})
export class Postular {
  rq: any;
  nombre = '';
  apellido = '';
  dni = '';
  correo = '';
  telefono = '';
  medioPreferido = 'whatsapp';
  comentarios = '';
  cvName = '';
  message = '';
  errorDni = '';
  errorEmail = '';

  constructor(
    private route: ActivatedRoute,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  onFileChange(event: any) {
    const file = event.target.files?.[0];
    if (file) {
      this.cvName = file.name;
    }
  }

  validateDni() {
    if (this.dni && this.dni.length !== 8) {
      this.errorDni = 'El DNI debe tener 8 dígitos';
    } else {
      this.errorDni = '';
    }
  }

  validateEmail() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (this.correo && !emailRegex.test(this.correo)) {
      this.errorEmail = 'El correo debe ser válido';
    } else {
      this.errorEmail = '';
    }
  }

  isFormValid(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return (
      this.nombre.trim() !== '' &&
      this.apellido.trim() !== '' &&
      this.dni.trim().length === 8 &&
      /^[0-9]{8}$/.test(this.dni) &&
      emailRegex.test(this.correo) &&
      this.telefono.trim() !== '' &&
      !this.errorDni &&
      !this.errorEmail
    );
  }

  enviar() {
    if (!this.rq) {
      return;
    }

    if (!this.isFormValid()) {
      alert('Completa todos los campos obligatorios correctamente.');
      return;
    }

    this.rqService.addCandidate(this.rq.codigo, {
      nombre: this.nombre,
      apellido: this.apellido,
      dni: this.dni,
      correo: this.correo,
      telefono: this.telefono,
      medioPreferido: this.medioPreferido,
      comentarios: this.comentarios,
      cvName: this.cvName
    });

    this.message = 'Tu postulación se envió correctamente. Gracias por postular.';
    this.nombre = '';
    this.apellido = '';
    this.dni = '';
    this.correo = '';
    this.telefono = '';
    this.medioPreferido = 'whatsapp';
    this.comentarios = '';
    this.cvName = '';
    this.errorDni = '';
    this.errorEmail = '';
  }
}