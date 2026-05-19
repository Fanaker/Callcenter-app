/**
 * Modelo mejorado de Candidato
 * Incluye validación: Solo se puede marcar entrevista como "Sí" si Apto = "Sí"
 */

export interface Candidato {
  id?: string;
  dni?: string;
  nombre: string;
  apellido: string;
  email: string;
  correo?: string;
  telefono: string;
  puesto: string;
  medioPreferido?: string;
  cvUrl?: string;
  fechaPostulacion: Date;
  apto: 'si' | 'no' | null; // Evaluación de aptitud
  entrevista: 'si' | 'no' | null; // Resultado de entrevista (validado)
  observaciones?: string;
  fechaEntrevista?: Date;
  evaluador?: string;
  estado: 'pendiente' | 'en_evaluacion' | 'finalizado';
}

/**
 * DTO para validación de cambios
 */
export interface CandidatoValidationDTO {
  aptoValue: 'si' | 'no' | null;
  entrevistaValue: 'si' | 'no' | null;
}