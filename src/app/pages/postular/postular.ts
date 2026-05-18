import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';

import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';

@Component({
  selector: 'app-postular',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './postular.html',
  styleUrl: './postular.css'
})
export class Postular {
  rq: Rq | undefined;

  nombre = '';
  apellido = '';
  dni = '';
  correo = '';
  telefono = '';
  medioPreferido: 'whatsapp' | 'llamada' | 'email' = 'whatsapp';
  cvUrl = '';
  comentarios = '';

  message = '';
  errorDni = '';
  errorEmail = '';
  errorCvUrl = '';

  constructor(
    private route: ActivatedRoute,
    private rqService: RqService
  ) {
    const codigo = this.route.snapshot.paramMap.get('codigo') || '';
    this.rq = this.rqService.getByCodigo(codigo);
  }

  get formularioBloqueado(): boolean {
    return !this.rq || this.rq.estado === 'CERRADO';
  }

  validateDni(): void {
    const dniRegex = /^[0-9]{8}$/;

    if (this.dni && !dniRegex.test(this.dni)) {
      this.errorDni = 'El DNI debe tener exactamente 8 dígitos numéricos.';
    } else {
      this.errorDni = '';
    }
  }

  validateEmail(): void {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (this.correo && !emailRegex.test(this.correo)) {
      this.errorEmail = 'El correo debe ser válido.';
    } else {
      this.errorEmail = '';
    }
  }

  validateCvUrl(): void {
    const url = this.cvUrl.trim();

    if (!url) {
      this.errorCvUrl = 'Debes ingresar el enlace de tu CV.';
      return;
    }

    if (!url.startsWith('https://')) {
      this.errorCvUrl = 'El enlace del CV debe iniciar con https://';
      return;
    }

    if (!url.includes('drive.google.com')) {
      this.errorCvUrl = 'El enlace debe ser de Google Drive.';
      return;
    }

    this.errorCvUrl = '';
  }

  isFormValid(): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const dniRegex = /^[0-9]{8}$/;
    const cvUrl = this.cvUrl.trim();

    return (
      !!this.rq &&
      this.rq.estado === 'ABIERTO' &&
      this.nombre.trim() !== '' &&
      this.apellido.trim() !== '' &&
      dniRegex.test(this.dni) &&
      emailRegex.test(this.correo) &&
      this.telefono.trim() !== '' &&
      cvUrl !== '' &&
      cvUrl.startsWith('https://') &&
      cvUrl.includes('drive.google.com') &&
      !this.errorDni &&
      !this.errorEmail &&
      !this.errorCvUrl
    );
  }

  enviar(): void {
    if (!this.rq) {
      alert('No se encontró el requerimiento.');
      return;
    }

    if (this.rq.estado === 'CERRADO') {
      alert('Este requerimiento ya está cerrado. No se pueden registrar más postulantes.');
      return;
    }

    this.validateDni();
    this.validateEmail();
    this.validateCvUrl();

    if (!this.isFormValid()) {
      alert('Completa todos los campos obligatorios correctamente.');
      return;
    }

    this.rqService.addCandidate(this.rq.codigo, {
      nombre: this.nombre.trim(),
      apellido: this.apellido.trim(),
      dni: this.dni.trim(),
      correo: this.correo.trim(),
      telefono: this.telefono.trim(),
      medioPreferido: this.medioPreferido,
      cvUrl: this.cvUrl.trim(),
      comentarios: this.comentarios.trim()
    });

    this.message = 'Tu postulación se envió correctamente. Gracias por postular.';

    this.nombre = '';
    this.apellido = '';
    this.dni = '';
    this.correo = '';
    this.telefono = '';
    this.medioPreferido = 'whatsapp';
    this.cvUrl = '';
    this.comentarios = '';
    this.errorDni = '';
    this.errorEmail = '';
    this.errorCvUrl = '';
  }
}