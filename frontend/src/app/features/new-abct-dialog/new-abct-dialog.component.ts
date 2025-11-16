import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-new-abct-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule
  ],
  templateUrl: './new-abct-dialog.component.html',
  styleUrl: './new-abct-dialog.component.scss'
})
export class NewAbctDialogComponent {
  abctForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<NewAbctDialogComponent>
  ) {
    this.abctForm = this.fb.group({
      abctName: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(100)]]
    });
  }

  onSubmit(): void {
    if (this.abctForm.valid) {
      const abctName = this.abctForm.value.abctName.trim();
      this.dialogRef.close(abctName);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  getErrorMessage(): string {
    const control = this.abctForm.get('abctName');
    if (control?.hasError('required')) {
      return 'ABCT name is required';
    }
    if (control?.hasError('minlength')) {
      return 'ABCT name must be at least 2 characters';
    }
    if (control?.hasError('maxlength')) {
      return 'ABCT name must not exceed 100 characters';
    }
    return '';
  }
}
