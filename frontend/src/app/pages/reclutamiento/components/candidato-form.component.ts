import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Candidato } from '../models/candidato.model';
import { CandidatoService } from '../services/candidato.service';
import { ReclutamientoValidadorService } from '../services/reclutamiento-validador.service';

/**
 * Componente para crear/editar candidatos
 * Incluye validación de la regla: Entrevista "Sí" solo si Apto = "Sí"
 */
@Component({
  selector: 'app-candidato-form',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './candidato-form.component.html',
  styleUrls: ['./candidato-form.component.css']
})
export class CandidatoFormComponent implements OnInit {
  @Input() candidato: Candidato | null = null;
  @Output() guardar = new EventEmitter<Candidato>();
  @Output() cancelar = new EventEmitter<void>();

  formulario: FormGroup;
  esEdicion = false;
  mostrarResumenValidacion = false;

  constructor(
    private fb: FormBuilder,
    private candidatoService: CandidatoService,
    private validador: ReclutamientoValidadorService
  ) {
    this.formulario = this.crearFormulario();
  }

  ngOnInit(): void {
    if (this.candidato) {
      this.esEdicion = true;
      this.formulario.patchValue(this.candidato);
    }
  }

  /**
   * Crea el formulario reactivo
   */
  private crearFormulario(): FormGroup {
    return this.fb.group({
      nombre: ['', [Validators.required]],
      apellido: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      telefono: ['', [Validators.required]],
      puesto: ['', [Validators.required]],
      fechaPostulacion: [new Date(), [Validators.required]],
      apto: [null],
      entrevista: [null],
      fechaEntrevista: [null],
      observaciones: [''],
      estado: ['pendiente', [Validators.required]],
      evaluador: ['']
    });
  }

  /**
   * Verifica si se puede marcar entrevista como "Sí"
   */
  puedeMarcarEntrevista(): boolean {
    const aptoValue = this.formulario.get('apto')?.value;
    return this.validador.esEntrevistaHabilitada(aptoValue);
  }

  /**
   * Maneja cambios en el campo Apto
   */
  onAptoChange(): void {
    const aptoValue = this.formulario.get('apto')?.value;
    const entrevistaValue = this.formulario.get('entrevista')?.value;

    // Si apto cambia a "no", forzar entrevista a "no"
    if (aptoValue === 'no') {
      this.formulario.patchValue({ entrevista: 'no' });
      this.mostrarResumenValidacion = true;
    }
    // Si apto es null y entrevista es "si", cambiar entrevista a null
    else if (aptoValue === null && entrevistaValue === 'si') {
      this.formulario.patchValue({ entrevista: null });
      this.mostrarResumenValidacion = true;
    }

    // Desactivar el campo si no puede marcar entrevista
    if (!this.puedeMarcarEntrevista()) {
      this.formulario.get('entrevista')?.disable();
    } else {
      this.formulario.get('entrevista')?.enable();
    }
  }

  /**
   * Maneja cambios en el campo Entrevista
   */
  onEntrevistaChange(): void {
    const entrevistaValue = this.formulario.get('entrevista')?.value;
    const aptoValue = this.formulario.get('apto')?.value;

    // Validación: No permitir "si" en entrevista si apto != "si"
    if (entrevistaValue === 'si' && aptoValue !== 'si') {
      this.formulario.patchValue({ entrevista: null });
      console.warn('No se puede marcar entrevista como "Sí" sin que Apto sea "Sí"');
    }

    this.mostrarResumenValidacion = true;
  }

  /**
   * Maneja el envío del formulario
   */
  onSubmit(): void {
    if (!this.formulario.valid) {
      return;
    }

    const candidatoData = this.formulario.getRawValue();
    this.guardar.emit(candidatoData);
  }

  /**
   * Cancela el formulario
   */
  onCancel(): void {
    this.cancelar.emit();
  }
}