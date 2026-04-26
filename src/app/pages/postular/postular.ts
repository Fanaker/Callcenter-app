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

  enviar() {
    if (!this.rq) {
      return;
    }

    const dniValido = /^[0-9]{1,8}$/.test(this.dni.trim());
    if (!this.nombre.trim() || !this.apellido.trim() || !this.dni.trim() || !this.correo.trim() || !this.telefono.trim()) {
      alert('Completa todos los campos obligatorios.');
      return;
    }

    if (!dniValido) {
      alert('El DNI debe tener hasta 8 números.');
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
  }
}