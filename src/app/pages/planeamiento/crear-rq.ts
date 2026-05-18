import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RqService } from '../../services/rq';
import { Rq } from '../../models/rq.model';

@Component({
  selector: 'app-crear-rq',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './crear-rq.html',
  styleUrl: './crear-rq.css'
})
export class CrearRq {
  campaign = '';
  puesto = '';
  cantidad = 0;
  fechaIngreso = '';
  fechaFinCapacitacion = '';
  fechaInicioCapacitacion = '';
  diasCapacitacion = 0;
  comentarios = '';

  // Mensajes de error
  errorFechaFinCapacitacion = '';
  errorFechaInicioCapacitacion = '';

  constructor(private rqService: RqService, private router: Router) {}

  crearRQ() {
    // Limpiar mensajes de error previos
    this.errorFechaFinCapacitacion = '';
    this.errorFechaInicioCapacitacion = '';

    if (!this.validarRQ()) {
      return;
    }

    const rq: Partial<Rq> = {
      codigo: this.rqService.generateCode(),
      campaign: this.campaign,
      puesto: this.puesto,
      comentarios: this.comentarios,
      cantidad: this.cantidad,
      diasCapacitacion: this.diasCapacitacion,
      fechaIngreso: this.fechaIngreso,
      fechaInicioCapacitacion: this.fechaInicioCapacitacion,
      fechaFinCapacitacion: this.fechaFinCapacitacion,
      estado: 'ABIERTO'
    };

    this.rqService.add(rq);
    this.router.navigate(['/planeamiento']);
  }

  validarRQ(): boolean {
    let isValid = true;

    // Validar campos requeridos
    if (
      this.campaign.trim() === '' ||
      this.cantidad <= 0 ||
      this.puesto.trim() === '' ||
      this.fechaIngreso === '' ||
      this.fechaFinCapacitacion === '' ||
      this.fechaInicioCapacitacion === '' ||
      this.diasCapacitacion <= 0
    ) {
      alert('❌ Completa todos los campos correctamente');
      return false;
    }

    // Validar fechas
    const fechaIngreso = new Date(this.fechaIngreso);
    const fechaFin = new Date(this.fechaFinCapacitacion);
    const fechaInicioCap = new Date(this.fechaInicioCapacitacion);
    const diaMs = 24 * 60 * 60 * 1000;

    // Validar que fecha fin capacitación < fecha ingreso
    if (fechaFin >= fechaIngreso) {
      this.errorFechaFinCapacitacion = 'La fecha de fin de capacitación debe ser anterior a la fecha prevista de inicio del personal.';
      isValid = false;
    } else {
      this.errorFechaFinCapacitacion = '';
    }

    // Validar que fecha inicio capacitación sea al menos 3 días antes de fecha fin capacitación
    if (fechaFin.getTime() - fechaInicioCap.getTime() < 3 * diaMs) {
      this.errorFechaInicioCapacitacion = 'La fecha de inicio de capacitación debe ser al menos 3 días anterior a la fecha de fin de capacitación.';
      isValid = false;
    } else {
      this.errorFechaInicioCapacitacion = '';
    }

    return isValid;
  }

  // Método para validar en tiempo real
  onFechaChange() {
    if (this.fechaIngreso && this.fechaFinCapacitacion) {
      const fechaIngreso = new Date(this.fechaIngreso);
      const fechaFin = new Date(this.fechaFinCapacitacion);

      if (fechaFin >= fechaIngreso) {
        this.errorFechaFinCapacitacion = 'La fecha de fin de capacitación debe ser anterior a la fecha prevista de inicio del personal.';
      } else {
        this.errorFechaFinCapacitacion = '';
      }
    }

    if (this.fechaInicioCapacitacion && this.fechaFinCapacitacion) {
      const fechaInicioCap = new Date(this.fechaInicioCapacitacion);
      const fechaFin = new Date(this.fechaFinCapacitacion);
      const diaMs = 24 * 60 * 60 * 1000;

      if (fechaFin.getTime() - fechaInicioCap.getTime() < 3 * diaMs) {
        this.errorFechaInicioCapacitacion = 'La fecha de inicio de capacitación debe ser al menos 3 días anterior a la fecha de fin de capacitación.';
      } else {
        this.errorFechaInicioCapacitacion = '';
      }
    }
  }
}